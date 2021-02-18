#!/usr/bin/env python
#
# heatmap ds ChRIS plugin app
#
# (c) 2021 Fetal-Neonatal Neuroimaging & Developmental Science Center
#                   Boston Children's Hospital
#
#              http://childrenshospital.org/FNNDSC/
#                        dev@babyMRI.org
#

from    chrisapp.base   import ChrisApp

import  os
import  glob

import  numpy                               as np
from    matplotlib      import pyplot       as plt
from    skimage.io      import imread
from    skimage.metrics import structural_similarity    as ssim
import  cv2
import  imutils

import  inspect
import  json

import  pudb

Gstr_title = """
 _                _
| |              | |
| |__   ___  __ _| |_ _ __ ___   __ _ _ __
| '_ \ / _ \/ _` | __| '_ ` _ \ / _` | '_ \.
| | | |  __/ (_| | |_| | | | | | (_| | |_) |
|_| |_|\___|\__,_|\__|_| |_| |_|\__,_| .__/
                                     | |
                                     |_|
"""

Gstr_synopsis = """

    NAME

       heatmap

    SYNOPSIS

        heatmap                                                         \\
            [-h] [--help]                                               \\
            [--json]                                                    \\
            [--man]                                                     \\
            [--meta]                                                    \\
            [--savejson <DIR>]                                          \\
            [-v <level>] [--verbosity <level>]                          \\
            [--version]                                                 \\
            [--inputSubDir1 <sample1Dir>]                               \\
            [--inputFilt1 <inputFilt1>]                                 \\
            [--inputSubDir2 <sample2Dir>]                               \\
            [--inputFilt2 <inputFilt2>]                                 \\
            <inputDir>                                                  \\
            <outputDir>

    BRIEF EXAMPLE

        * Bare bones execution

        # Assume that $PWD/in/dir1 has png files
        # Assume that $PWD/in/dir2 has png files
        docker run --rm -u $(id -u)                                     \\
                -v $(pwd)/in:/incoming -v $(pwd)/out:/outgoing          \\
                fnndsc/pl-heatmap heatmap                               \\
                --inputSubDir1  dir1                                    \\
                --inputFilt1    png                                     \\
                --inputSubDir2  dir2                                    \\
                --inputFilt2    png                                     \\
                /incoming /outgoing

    DESCRIPTION

        ``heatmap`` is a ChRIS DS plugin that determines the "difference"
        between two image sets and generates several output image types
        and measures.

        Output images are stored in a per-slice manner in the following
        subdirectories of <outputDir>:

            * heatmap       -   the actual heatmap difference
            * threshold     -   thresholded difference
            * contourA      -   difference rectangles on image A
            * contourB      -   difference rectangles on image B

        Output measure per image slice:

            * Structural Similarity Index, stored as JSON return.

        The module assumes that each image set has the same number of
        constituent images (or slices) and that each constituent image
        corresponding between the two sets is the same size.

        The module tries to make some reasonable choices in cases when these
        assumptions are not met, with appropriate reporting.

        Note, most the guts are adapted from Adrian Rosebrock's most excellent
        post:

        https://www.pyimagesearch.com/2017/06/19/image-difference-with-opencv-and-python/

    ARGS

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


"""

class Heatmap(ChrisApp):
    """
    A ChRIS DS plugin that compares two different image sets and
    generates useful difference image data and metrics.
    """
    PACKAGE                 = __package__
    TITLE                   = 'A heatmap generating app'
    CATEGORY                = ''
    TYPE                    = 'ds'
    ICON                    = '' # url of an icon image
    MAX_NUMBER_OF_WORKERS   = 1  # Override with integer value
    MIN_NUMBER_OF_WORKERS   = 1  # Override with integer value
    MAX_CPU_LIMIT           = '' # Override with millicore value as string, e.g. '2000m'
    MIN_CPU_LIMIT           = '' # Override with millicore value as string, e.g. '2000m'
    MAX_MEMORY_LIMIT        = '' # Override with string, e.g. '1Gi', '2000Mi'
    MIN_MEMORY_LIMIT        = '' # Override with string, e.g. '1Gi', '2000Mi'
    MIN_GPU_LIMIT           = 0  # Override with the minimum number of GPUs, as an integer, for your plugin
    MAX_GPU_LIMIT           = 0  # Override with the maximum number of GPUs, as an integer, for your plugin

    # Use this dictionary structure to provide key-value output descriptive information
    # that may be useful for the next downstream plugin. For example:
    #
    # {
    #   "finalOutputFile":  "final/file.out",
    #   "viewer":           "genericTextViewer",
    # }
    #
    # The above dictionary is saved when plugin is called with a ``--saveoutputmeta``
    # flag. Note also that all file paths are relative to the system specified
    # output directory.
    OUTPUT_META_DICT = {}

    def method_name(self):
        return inspect.stack()[1][3]

    def define_parameters(self):

        """
        Define the CLI arguments accepted by this plugin app.
        Use self.add_argument to specify a new app argument.
        """

        self.add_argument('--inputSubDir1',
            dest        = 'str_inputSubDir1',
            type        = str,
            optional    = False,
            default     = "",
            help        = 'Subdirectory (within <inputDir>) containing 1st image set'
        )
        self.add_argument('--imageFilt1',
            dest        = 'str_imageFilt1',
            type        = str,
            optional    = True,
            default     = "png",
            help        = "Some string filter on the first image file"
        )
        self.add_argument('--inputSubDir2',
            dest        = 'str_inputSubDir2',
            type        = str,
            optional    = False,
            default     = "",
            help        = 'Subdirectory (within <inputDir>) containing 2nd image set'
        )
        self.add_argument('--imageFilt2',
            dest        = 'str_imageFilt2',
            type        = str,
            optional    = True,
            default     = "png",
            help        = "Some string filter on the second image file"
        )

    def imageFileNames_determine(self, options) -> dict:
        """
        Simply just determines the names of files to load
        from the filesystem.
        """
        b_status    :   bool    = False
        imageAcount :   int     = 0
        imageBcount :   int     = 0

        print("\n--->Determining list of image filenames<---")

        print("%-75s" % ("Image set A (%s)... " % options.str_inputSubDir1), end = "")
        for entry in sorted(os.scandir(
           os.path.join(options.inputdir, options.str_inputSubDir1)
            ), key=lambda e: e.name):
            if options.str_imageFilt1 in entry.name:
                str_fileA = entry.path
                self.lstr_imageAfiles.append(str_fileA)
                # print("Adding %s" % str_fileA)
                imageAcount += 1
        print("%d images"  % imageAcount)

        print("%-75s" % ("Image set B (%s)... " % options.str_inputSubDir2), end = "")
        for entry in sorted(os.scandir(
           os.path.join(options.inputdir, options.str_inputSubDir2)
            ), key=lambda e: e.name):
            if options.str_imageFilt2 in entry.name:
                str_fileB = entry.path
                self.lstr_imageBfiles.append(str_fileB)
                # print("Adding %s" % str_fileB)
                imageBcount += 1
        print("%d images"  % imageBcount)

        # This remainder is just for return message status and reporting
        if imageAcount and imageBcount:
            if imageAcount == imageBcount:
                b_status = True
                str_message  = \
                "Successfully determined image files to load and checks pass"
            else:
                str_message  = \
                "Image sets have differing numbers of constituent images, %d and %d" % \
                    (imageAcount, imageBcount)
        else:
            str_message  = \
            "At least one image set was empty, %d and %d" % \
                (imageAcount, imageBcount)

        return {
            'status':   b_status,
            'method':   self.method_name(),
            'message':  str_message,
            'sizeSetA': imageAcount,
            'sizeSetB': imageBcount
        }

    def imageSlices_populate(self, options, d_prior)  -> dict:
        """
        Populate each image slice with a cv2 "image"/"matrix".

        This method is probably what needs to be factored for
        reading mgz vol slices into the image list.
        """

        fileCount   :   int     = 0
        b_status    :   bool    = False

        print("\n--->Reading actual image files<---")
        if d_prior['status']:
            print("%-75s" % "loading image set A and set B... ", end = "")
            for (str_fileA, str_fileB) in zip(  self.lstr_imageAfiles,
                                                self.lstr_imageBfiles):
                b_status                        = True
                self.l_imageA.append(cv2.imread(str_fileA))
                self.l_imageB.append(cv2.imread(str_fileB))
                fileCount += 1
            print("%d files read." % fileCount)

        return {
            'status':       b_status,
            'method':       self.method_name(),
            'readCount':    fileCount,
            'd_stack':      d_prior
        }

    def imageSlices_toGrayScale(self, options, d_prior)  -> dict:
        """
        Convert each image slice to gray scale.
        """

        b_status    :   bool    = False
        fileCount   :   int     = 0
        i           :   int     = 0

        print("\n--->Converting to grayScale<---")
        if d_prior['status']:
            print("%-75s" % "converting image set A and set B... ", end = "")
            for i in range(0, len(self.l_imageA)):
                b_status                = True
                self.l_imageAgray.append(
                    cv2.cvtColor(   self.l_imageA[i],
                                    cv2.COLOR_BGR2GRAY)
                )
                self.l_imageBgray.append(
                    cv2.cvtColor( self.l_imageB[i],
                                  cv2.COLOR_BGR2GRAY)
                )
            print("%d images converted." % i)

        return {
            'status':   b_status,
            'method':   self.method_name(),
            'd_stack':  d_prior
        }

    def grayScale_slicesProcess(self, options, d_prior):
        """
        The core of this plugin.
        """
        b_status    :   bool    = False
        i           :   int     = 0

        print("\n--->Processing grayScale slices<---")
        if d_prior['status']:
            print("%-75s" % "calculating... ", end = "")
            for i in range(0, len(self.l_imageA)):
                b_status                = True
                # print("Calculating difference for slice  %3d..." % i)
                (score, imdiff)         = ssim(
                                                self.l_imageAgray[i],
                                                self.l_imageBgray[i],
                                                full = True
                                        )
                # convert normalized float imdiff to integer ranges
                self.l_imageDiff.append((imdiff * 255).astype("uint8"))
                self.l_SSIM.append(score)

                # print("Thresholding and contouring slice %3d..." % i)
                self.l_imageThresh.append(cv2.threshold(
                    self.l_imageDiff[i], 0, 255,
                    cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
                )
                # print("Contouring slice                  %3d..." % i)
                contour     = cv2.findContours(
                    self.l_imageThresh[i].copy(),
                    cv2.RETR_EXTERNAL,
                    cv2.CHAIN_APPROX_SIMPLE
                )
                self.l_imageContour.append(imutils.grab_contours(contour))
            print("difference, threshold, and contour.")

        return {
            'status':   b_status,
            'method':   self.method_name(),
            'd_stack':  d_prior
        }

    def outputs_generate(self, options, d_prior):
        """
        Save all the relevant output images and JSON data.
        """
        b_status        :   bool    = False
        str_baseoutput  :   str     = ""

        print("\n--->Saving outputs<---")
        if d_prior['status']:
            for str_dir in self.lstr_outputDirs:
                str_outputPath  = os.path.join(options.outputdir, str_dir)
                os.makedirs(str_outputPath, exist_ok = True)
                print("%-75s" % ("Saving computed image slices for %s... " % str_outputPath), end = "")
                for i in range(0, len(self.l_imageA)):
                    b_status                = True
                    str_outputImageFile     = "%s/slice-%03d.png" % (str_outputPath, i)
                    if str_dir == 'naive':
                        imageA      = self.l_imageA[i]
                        imageB      = self.l_imageB[i]
                        imageC      = np.abs(imageA - imageB)
                        heatmap     = cv2.applyColorMap(imageC, cv2.COLORMAP_HOT)
                        cv2.imwrite(str_outputImageFile, heatmap)
                    if str_dir == 'heatmap':
                        image       = self.l_imageDiff[i]
                        heatmap     = cv2.applyColorMap(image, cv2.COLORMAP_HOT)
                        cv2.imwrite(str_outputImageFile, heatmap)
                    if str_dir == 'threshold':
                        image       = self.l_imageThresh[i]
                        cv2.imwrite(str_outputImageFile, image)
                    if str_dir == 'contourA' or str_dir == 'contourB':
                        if str_dir == 'contourA':   image   = self.l_imageA[i]
                        if str_dir == 'contourB':   image   = self.l_imageB[i]
                        for c in self.l_imageContour[i]:
                            (x, y, w, h) = cv2.boundingRect(c)
                            cv2.rectangle(
                                            image,
                                            (x, y), (x + w, y + h),
                                            (0, 0, 255), 2
                                        )
                            cv2.imwrite(str_outputImageFile, image)
                print("done.")
            with open('%s/SSIN.json' % options.outputdir, 'w')  as jsonfile:
                json.dump(self.l_SSIM, jsonfile, indent = 4)

        return {
            'status':   b_status,
            'method':   self.method_name(),
            'd_stack':  d_prior
        }


    def run(self, options):
        """
        Define the code to be run by this plugin app.
        """

        print(Gstr_title)
        print('Version: %s' % self.get_version())

        d_options = vars(options)
        for k,v in d_options.items():
            print("%20s: %-40s" % (k, v))
        print("")

        # For future expansion, if reading mgz files,
        # skip the image file reading (obviously) and
        # use and mgz appropriate method to read in the
        # volume. Then, store each "slice" of the volume
        # into the
        #
        #           self.l_image[A|B]gray
        #
        # appropriately. The grayScale "list" of slices
        # is the core driver of the difference map. It
        # might be necessary to convert the mgz slice to
        # an appropriate cv2 image structure:
        #
        #  img_cv  = cv2.resize(<mgzSlice_as_np>,(256,256))
        #
        # Most likely entry method to refactor is the
        #           self.imageSlices_populate()
        #

        d_run                   :   dict    = {}

        # Image A data structures -- input 1:
        self.lstr_imageAfiles   :   list    = []
        self.l_imageA           :   list    = []
        self.l_imageAgray       :   list    = []

        # Image B data structures -- input 2:
        self.lstr_imageBfiles   :   list    = []
        self.l_imageB           :   list    = []
        self.l_imageBgray       :   list    = []

        # Processed data structures -- output:
        self.lstr_imageOutfiles :   list    = []
        self.l_imageDiff        :   list    = []
        self.l_imageThresh      :   list    = []
        self.l_imageContour     :   list    = []
        self.l_SSIM             :   list    = []

        self.lstr_outputDirs    :   list    = ['naive', 'heatmap', 'threshold', 'contourA', 'contourB']
        d_run = self.outputs_generate(options,
                    self.grayScale_slicesProcess(options,
                        self.imageSlices_toGrayScale(options,
                            self.imageSlices_populate(options,
                                self.imageFileNames_determine(options)
                            )
                        )
                    )
                )
        with open('%s/run.json' % options.outputdir, 'w') as jsonrun:
            json.dump(d_run, jsonrun, indent = 4)

    def show_man_page(self):
        """
        Print the app's man page.
        """

        print(Gstr_synopsis)
