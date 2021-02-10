.. code:: console
     _                _
    | |              | |
    | |__   ___  __ _| |_ _ __ ___   __ _ _ __
    | '_ \ / _ \/ _` | __| '_ ` _ \ / _` | '_ \
    | | | |  __/ (_| | |_| | | | | | (_| | |_) |
    |_| |_|\___|\__,_|\__|_| |_| |_|\__,_| .__/
                                         | |
                                         |_|



pl-heatmap
================================

.. image:: https://travis-ci.org/FNNDSC/heatmap.svg?branch=master
    :target: https://travis-ci.org/FNNDSC/heatmap

.. image:: https://img.shields.io/badge/python-3.8%2B-blue.svg
    :target: https://github.com/FNNDSC/pl-heatmap/blob/master/setup.py

.. contents:: Table of Contents


Abstract
--------

A ChRIS DS plugin that compares two different image sets and generates useful difference image data and metrics.


Description
-----------

``heatmap`` is a ChRIS DS plugin that determines the "difference" between two image sets and generates several output image types and measures.

Output images are stored in a per-slice manner in the following subdirectories of <outputDir>:

    * heatmap       -   the actual heatmap difference
    * threshold     -   thresholded difference
    * contourA      -   difference rectangles on image A
    * contourB      -   difference rectangles on image B

Output measure per image slice:

    * Structural Similarity Index, stored as JSON return.

The module assumes that each image set has the same number of constituent images (or slices) and that each constituent image corresponding between the two sets is the same size.

The module tries to make some reasonable choices in cases when these assumptions are not met, with appropriate reporting.

Note, most the guts are adapted from Adrian Rosebrock's most excellent post:

https://www.pyimagesearch.com/2017/06/1image-difference-with-opencv-and-python/


Usage
-----

.. code:: console

        heatmap                                                         \
            [-h] [--help]                                               \
            [--json]                                                    \
            [--man]                                                     \
            [--meta]                                                    \
            [--savejson <DIR>]                                          \
            [-v <level>] [--verbosity <level>]                          \
            [--version]                                                 \
            [--inputSubDir1 <sample1Dir>]                               \
            [--inputFilt1 <inputFilt1>]                                 \
            [--inputSubDir2 <sample2Dir>]                               \
            [--inputFilt2 <inputFilt2>]                                 \
            <inputDir>                                                  \
            <outputDir>


Arguments
~~~~~~~~~

.. code::

        [-h] [--help]
        If specified, show help message and exit.

        [--json]
        If specified, show json representation of app and exit.

        [--man]
        If specified, print (this) man page and exit.

        [--meta]
        If specified, print plugin meta data and exit.

        [--savejson <DIR>]
        If specified, save json representation file to DIR and exit.

        [-v <level>] [--verbosity <level>]
        Verbosity level for app. Not used currently.

        [--version]
        If specified, print version number and exit.

        [--jsonReturn]
        If specified, return a JSON description of the run.

        [--inputSubDir1 <sample1Dir>]
        The name of the subdirectory within the <inputDir> that contains
        the first set of images.

        [--imageFilt1 <imageFilt1>]
        The type of the images in <sample1Dir>.

        [--inputSubDir <sample2Dir>]
        The name of the subdirectory within the <inputDir> that contains
        the second set of images.

        [--imageFilt2 <imageFilt2>]
        The type of the images in <sample2Dir>.


Getting inline help is:

.. code:: bash

    docker run --rm fnndsc/pl-heatmap heatmap --man

Development
-----------

Build the Docker container:

.. code:: bash

    docker build -t local/pl-heatmap .


Python dependencies can be added to ``setup.py``. After a successful build, track which dependencies you have installed by generating the `requirements.txt` file.

.. code:: bash

    docker run --rm local/pl-heatmap -m pip freeze > requirements.txt


For the sake of reproducible builds, be sure that ``requirements.txt`` is up to date before you publish your code.


.. code:: bash

    git add requirements.txt && git commit -m "Bump requirements.txt" && git push

Run
----

Assuming that we have image files in the ``in`` directory :

.. code:: bash

    mkdir in out && chmod 777 out
    docker run --rm -u $(id -u)                                             \
        -v $(pwd)/in:/incoming -v $(pwd)/out/:/outgoing                     \
        local/pl-heatmap heatmap.py                                         \
        --inputSubDir1  imageSet1                                           \
        --imageFilt1    png                                                 \
        --inputSubDir2  imageSet2                                           \
        --imageFilt2    png                                                 \
        /incoming /outgoing

Debug
-----

To debug the containerized version of this plugin, simply volume map the source directories of the repo into the relevant locations of the container image:

.. code:: bash

    docker run -ti --rm -v $PWD/in:/incoming:ro -v $PWD/out:/outgoing:rw    \
        -v $PWD/heatmap:/usr/local/lib/python3.9/site-packages/heatmap:ro   \
        local/pl-heatmap heatmap                                            \
        --inputSubDir1  imageSet1                                           \
        --imageFilt1    png                                                 \
        --inputSubDir2  imageSet2                                           \
        --imageFilt2    png                                                 \
        /incoming /outgoing

To enter the container:

.. code:: bash

    docker run -ti --rm -v $PWD/in:/incoming:ro -v $PWD/out:/outgoing:rw    \
        -v $PWD/heatmap:/usr/local/lib/python3.9/site-packages/heatmap:ro   \
        --entrypoint /bin/bash local/pl-pfdorun

Remember to use the ``-ti`` flag for interactivity!

*30*

.. image:: https://raw.githubusercontent.com/FNNDSC/cookiecutter-chrisapp/master/doc/assets/badge/light.png
    :target: https://chrisstore.co
