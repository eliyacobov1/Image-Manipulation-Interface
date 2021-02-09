from imageio import imread
import numpy as np
from skimage import color as sk
from scipy import signal
from matplotlib import pyplot as plt
import cv2


def read_image(filename, representation):
    im = imread(filename)
    im = im.astype('float64')
    im = im / 255
    if representation == 1 and len(im.shape) == 3:
        if im.shape[2] == 3:
            im = sk.rgb2gray(im)
        else:
            im = sk.rgb2gray(sk.rgba2rgb(im))
    return im


def im_to_uint8(im):
    return (im * 255).astype(np.uint8)


def im_display(filename, representation):
    plt.imshow(read_image(filename, representation),
               cmap=plt.cm.gray if representation == 1 else None)
    plt.show()


def is_rgb(im):
    """
    return True if image is of RGB format, False otherwise
    """
    return len(im.shape) == 3


def rgb2yiq(im_rgb):
    """
    convert a given RGB format image to corresponding YIQ format image
    """
    yiq_matrix = np.array([0.299, 0.587, 0.114,
                           0.596, -0.275, -0.321,
                           0.212, -0.523, 0.311]).reshape((3, 3))
    
    return im_rgb.reshape(-1, 3).dot(yiq_matrix.transpose()).reshape(im_rgb.shape)


def yiq2rgb(im_yiq):
    """
    convert a given YIQ format image to corresponding RGB format image
    """
    yiq_matrix = np.array([0.299, 0.587, 0.114,
                           0.596, -0.275, -0.321,
                           0.212, -0.523, 0.311]).reshape((3, 3))
    
    return im_yiq.reshape(-1, 3).dot(np.linalg.inv(yiq_matrix).transpose()).reshape(im_yiq.shape)


def normalize_hist(hist):
    """
    normalizes the values of the given histogram
    """
    c_m = np.min(hist[np.nonzero(hist)])
    norm_hist = np.vectorize(lambda value: round(((value - c_m) * 255) /
                                                 (np.amax(hist) - c_m)))
    return norm_hist(hist)


def get_hist(im):
    """
    returns the histogram of the given image
    """
    if is_rgb(im):
        im = rgb2yiq(im)[:, :, 0]
    im = (im * 255).round().astype(np.uint8)
    
    hist = np.histogram(im, np.arange(257))
    return hist[0]


def get_cumulative_hist(hist):
    """
    returns the cumulative histogram
    """
    return np.cumsum(hist)


def get_z_values(q_list):
    return np.append(np.append([-1], [((q_list[i - 1]) + round(q_list[i])) / 2 for i in range(1, len(q_list))]), [255])


def get_q_values(hist, z_list, n_quant):
    def f(i):
        return np.array(range(256)[int(np.floor(z_list[i])) + 1:
                                   int(np.floor(z_list[i + 1])) + 1])
    factor_by_hist = np.vectorize(lambda value: value * hist[value])
    
    return np.array([float(np.sum(factor_by_hist(f(i)))) /
                     np.sum(hist[f(i)]) for i in range(n_quant)])


def quantize(im_orig, n_quant, n_iter=5):
    """
    performs optimal quantization of a given grayscale or
     RGB image. @:returns a im_quant - the quantized output image
    """
    hist, iter_count = get_hist(im_orig), 0
    z_list = np.append(np.searchsorted(get_cumulative_hist(hist) / hist.sum(),
                                       np.linspace(0, 1, n_quant, endpoint=False)), [255])
    z_list[0] = -1
    q_list = get_q_values(hist, z_list, n_quant)
    
    while iter_count < n_iter:
        z_temp = get_z_values(q_list)
        if np.array_equal(z_list, z_temp):  # convergence
            break
        z_list = z_temp
        q_list = get_q_values(hist, z_list, n_quant)
        iter_count += 1
    
    map_scale = np.vectorize(lambda g: q_list[np.searchsorted(z_list, [int(round(g * 255))])[0] - 1] / 255)
    if is_rgb(im_orig):  # if RGB image
        im_yiq = rgb2yiq(im_orig)
        im_yiq[:, :, 0] = map_scale(im_yiq[:, :, 0])
        im_quant = yiq2rgb(im_yiq)
    else:  # if grey-scale image
        im_quant = map_scale(im_orig)
    return im_quant


def histogram_equalize(im):
    """
    performs histogram equalization on the given grayscale
     or RGB image and returns the transformed image
    """
    hist_orig = get_hist(im)
    hist_norm = normalize_hist(get_cumulative_hist(hist_orig))
    transformation = np.vectorize(lambda value: hist_norm[int(round(value * 255))] / 255)
    if is_rgb(im):  # convert RGB to YIQ
        im_yiq = rgb2yiq(im)
        im_yiq[:, :, 0] = transformation(im_yiq[:, :, 0])
        im_eq = yiq2rgb(im_yiq)
    else:
        im_eq = transformation(im)
    return im_eq


def conv_2d(im):
    """
    compute the magnitude of image derivatives using 2d convolution
    """
    dx = signal.convolve2d(im, np.array([[0.5, 0, -0.5]]), 'same')
    dy = signal.convolve2d(im, np.array([[0.5, 0, -0.5]]).T, 'same')
    magnitude = np.sqrt(np.abs(dx) ** 2 + np.abs(dy) ** 2)
    magnitude = np.where(magnitude > 0.03, 1.0, 0.0)
    return magnitude
