<p align="center" class="has-mb-6">
<img class="not-gallery-item" height="128" src="imgs/inkRasterPerspective_logo.svg" alt="logo">
<br><b>InkRasterPerspective</b></br>
<br>
Apply perspective transformations for raster images in Inkscape
<br>


# inkRasterPerspective

**inkRasterPerspective** is an Inkscape extension to apply perspective transformations to raster images, without the need to use external software. It works for both embedded and linked images.

# Installation

To install this extension, you can either use the extensions manager: (from the menu **Extensions** > **Manage Extensions...**), or follow the instructions below for manual installation.

## 1. Using the extensions manager:

Open Inkscape and go to **Extensions** > **Manage Extension...**. A separate window appears, click on the "Install Packages" tab, and type `InkRasterPerspective` within the search box and press <kbd>Enter</kbd>. Then click on the button "Install Package". These steps are illustrated below:

![Steps to install the InkRasterPerspective extension via the Extensions manager](imgs/Installation_via_extension_manager.png)

## 2. Manual Installation
If, for some reason, the installation via the extensions manager (as shown above) doesn't work, you can install the extension manually by following the instructions below:

### 2.1. On Linux:

```
cd $HOME/.config/inkscape/extensions
git clone https://github.com/s1291/InkRasterPerspective.git
```

* Open Inkscape (if it is already open, close then re-open it) and you should find the extension under: **Extensions** > **Raster Perspective** > **Perspective**.

### 2.2. On Windows:

* Download the most recent version (direct link: [zip](https://github.com/s1291/InkRasterPerspective/archive/refs/heads/master.zip))
* Extract it and copy the files `imagePerspective.py` and `imagePerspective.inx` to `C:\Program Files\Inkscape\share\inkscape\extensions`.


# How to use this extension

> This extension was tested with the following versions of Inkscape `1.2.x`, `1.3.x`, and `1.4`.

1. Select the raster image and the quadrangle path (envelope) . Make sure the envelope nodes are ordered as follows:

![order of enveloppe nodes](imgs/order_of_nodes.png)

For more details on how to find the nodes order for a path, check out this [post](https://graphicdesign.stackexchange.com/a/155289/147300).

2. **Extensions** > **Raster Perspective** > **Perspective**

See below:

![How to use the extension](imgs/howto.gif)

# License

Samir OUCHENE, 2021-2025

All code is licensed under the GNU General Public License version 3. See [the license file](https://github.com/s1291/InkRasterPerspective/blob/master/LICENSE) for details.
