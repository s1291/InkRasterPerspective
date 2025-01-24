#!/usr/bin/env python3

"""
Copyright (C) 2021-2025 Samir OUCHENE, samirmath01@gmail.com
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
02110-1301, USA.
"""

import os
import urllib.request
import urllib.parse

import io
import inkex
from PIL import Image as PIL_Image
import base64
import numpy


try:
    from base64 import decodebytes
except ImportError:
    from base64 import decodestring as decodebytes


class ImagePerspective(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)

    def extract_image(self, node):
        """Extract the node as if it were an image."""
        xlink = node.get("xlink:href")
        if not xlink.startswith("data:"):
            # Parse the path and get the absolute path of the image
            _path = urllib.parse.urlparse(xlink).path
            path = self.absolute_href(
                _path or "", cwd=os.path.dirname(self.options.input_file)
            )
            starts_with_file = xlink.startswith("file:")
            if starts_with_file or os.path.isfile(path):

                # FIXME: redundancy
                if starts_with_file:
                    path = urllib.parse.urlparse(xlink).path
                    # On windows it is important to use urllib.request.url2pathname
                    # see: https://stackoverflow.com/a/43925228/5920411
                    path = urllib.request.url2pathname(path)
                if os.path.isfile(path):
                    # open the file and encode it
                    # I know, this is a horrible workaround (to b64 encode the image), but
                    # for the sake of it, that provides an easy workaround for linked images,
                    # and let's ignore it for now. (#FIXME)
                    with open(path, "rb") as linked_img_file:
                        data = base64.b64encode(linked_img_file.read())
                        # return decodebytes(data.encode("utf-8"))
                        return decodebytes(data)

                else:
                    inkex.errormsg(f"Invalid path: {path}")

            return  # Not embedded image data

        try:
            data = xlink[5:]
            (_mimetype, data) = data.split(";", maxsplit=1)
            (base, data) = data.split(",", maxsplit=1)
        except ValueError:
            inkex.errormsg("Invalid image format found.")
            return

        if base != "base64":
            inkex.errormsg("Can't decode encoding: {}.".format(base))
            return

        return decodebytes(data.encode("utf-8"))

    def find_coeffs(self, source_coords, target_coords):
        matrix = []
        for s, t in zip(source_coords, target_coords):
            matrix.append([t[0], t[1], 1, 0, 0, 0, -s[0] * t[0], -s[0] * t[1]])
            matrix.append([0, 0, 0, t[0], t[1], 1, -s[1] * t[0], -s[1] * t[1]])
        A = numpy.array(matrix, dtype=float)
        B = numpy.array(source_coords).reshape(8)
        res = numpy.linalg.inv(A.T @ A) @ A.T @ B
        return numpy.array(res).reshape(8)

    def effect(self):
        the_image_node, envelope_node = self.svg.selection
        if str(envelope_node) == "image" and str(the_image_node) == "path":
            envelope_node, the_image_node = self.svg.selection  # switch
        if str(the_image_node) != "image" and str(envelope_node) != "path":
            inkex.errormsg(
                "Your selection must contain an image and a path with at least 4 points."
            )
            return
        img_width, img_height = the_image_node.width, the_image_node.height

        try:
            unit_to_vp = self.svg.unit_to_viewport
        except AttributeError:
            unit_to_vp = self.svg.uutounit

        try:
            vp_to_unit = self.svg.viewport_to_unit
        except AttributeError:
            vp_to_unit = self.svg.unittouu

        img_width = unit_to_vp(img_width)
        img_height = unit_to_vp(img_height)

        nodes_pts = list(envelope_node.path.control_points)
        node1 = (unit_to_vp(nodes_pts[0][0]), unit_to_vp(nodes_pts[0][1]))
        node2 = (unit_to_vp(nodes_pts[1][0]), unit_to_vp(nodes_pts[1][1]))
        node3 = (unit_to_vp(nodes_pts[2][0]), unit_to_vp(nodes_pts[2][1]))
        node4 = (unit_to_vp(nodes_pts[3][0]), unit_to_vp(nodes_pts[3][1]))

        nodes = [node1, node2, node3, node4]

        xMax = max([node[0] for node in nodes])
        xMin = min([node[0] for node in nodes])
        yMax = max([node[1] for node in nodes])
        yMin = min([node[1] for node in nodes])
        # add some assertions (FIXME)

        img_data = self.extract_image(the_image_node)
        orig_image = PIL_Image.open(io.BytesIO(img_data))
        pil_img_size = orig_image.size
        scale = pil_img_size[0] / img_width

        coeffs = self.find_coeffs(
            [
                (0, 0),
                (img_width * scale, 0),
                (img_width * scale, img_height * scale),
                (0, img_height * scale),
            ],
            [
                (node1[0] - xMin, node1[1] - yMin),
                (node2[0] - xMin, node2[1] - yMin),
                (node3[0] - xMin, node3[1] - yMin),
                (node4[0] - xMin, node4[1] - yMin),
            ],
        )

        W, H = xMax - xMin, yMax - yMin

        final_w, final_h = int(W), int(H)

        # Check if the image has transparency
        hasTransparency = orig_image.mode in ("RGBA", "LA") or (
            orig_image.mode == "P" and "transparency" in orig_image.info
        )

        transp_img = orig_image

        # If the original image is not transparent, create a new image with alpha channel
        if not hasTransparency:
            transp_img = PIL_Image.new("RGBA", orig_image.size)
            transp_img.format = "PNG"
            transp_img.paste(orig_image)

        # It was announced in pillow v9.1.0 that PIL.Image.PERSPECTIVE and PIL.Image.BICUBIC were 
        # deprecated and would be removed in v10.0 
        # see:  https://pillow.readthedocs.io/en/stable/releasenotes/9.1.0.html#deprecations
        #
        # However, that decision was reversed in v9.4.0 and those constants are kept.
        # https://pillow.readthedocs.io/en/stable/releasenotes/9.4.0.html#restored-image-constants
        image = transp_img.transform(
            (final_w, final_h),
            PIL_Image.PERSPECTIVE,
            coeffs,
            PIL_Image.BICUBIC,
        )

        obj = inkex.Image()
        obj.set("x", vp_to_unit(xMin))
        obj.set("y", vp_to_unit(yMin))
        obj.set("width", vp_to_unit(final_w))
        obj.set("height", vp_to_unit(final_h))
        # embed the transformed image
        persp_img_data = io.BytesIO()
        image.save(persp_img_data, transp_img.format)
        mime = PIL_Image.MIME[transp_img.format]
        b64 = base64.b64encode(persp_img_data.getvalue()).decode("utf-8")
        uri = f"data:{mime};base64,{b64}"
        obj.set("xlink:href", uri)
        self.svg.add(obj)


imagePerspective = ImagePerspective()
imagePerspective.run()
