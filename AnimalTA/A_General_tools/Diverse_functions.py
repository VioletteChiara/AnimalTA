import numpy as np
import random
from scipy.signal import savgol_filter
import psutil
import sys
import os


def low_priority(Low):
    """ Set the priority of the process to low/back to normal so that user's computer is not slow down/AnimalTA is faster."""
    priority = psutil.Process(os.getpid())
    try:
        sys.getwindowsversion()
    except AttributeError:
        isWindows = False
    else:
        isWindows = True

    if isWindows and Low:
        priority.nice(psutil.HIGH_PRIORITY_CLASS)
    elif isWindows and not Low:
        priority.nice(psutil.NORMAL_PRIORITY_CLASS)
    elif Low:
        priority.nice(10)
    else:
        priority.nice(0)
"""Demonstration of least-squares fitting of ellipses
    __author__ = "Ben Hammel, Nick Sullivan-Molina"
    __credits__ = ["Ben Hammel", "Nick Sullivan-Molina"]
    __maintainer__ = "Ben Hammel"
    __email__ = "bdhammel@gmail.com"
    __status__ = "Development"
    Requirements 
    ------------
    Python 2.X or 3.X
    numpy
    matplotlib
    References
    ----------
    (*) Halir, R., Flusser, J.: 'Numerically Stable Direct Least Squares 
        Fitting of Ellipses'
    (**) http://mathworld.wolfram.com/Ellipse.html
    (***) White, A. McHale, B. 'Faraday rotation data analysis with least-squares 
        elliptical fitting'
"""
class LSqEllipse:
    def fit(self, data):
        """Lest Squares fitting algorithm
        Theory taken from (*)
        Solving equation Sa=lCa. with a = |a b c d f g> and a1 = |a b c>
            a2 = |d f g>
        Args
        ----
        data (list:list:float): list of two lists containing the x and y data of the
            ellipse. of the form [[x1, x2, ..., xi],[y1, y2, ..., yi]]
        Returns
        ------
        coef (list): list of the coefficients describing an ellipse
           [a,b,c,d,f,g] corresponding to ax**2+2bxy+cy**2+2dx+2fy+g
        """
        x, y = np.asarray(data, dtype=float)

        # Quadratic part of design matrix [eqn. 15] from (*)
        D1 = np.mat(np.vstack([x ** 2, x * y, y ** 2])).T
        # Linear part of design matrix [eqn. 16] from (*)
        D2 = np.mat(np.vstack([x, y, np.ones(len(x))])).T

        # forming scatter matrix [eqn. 17] from (*)
        S1 = D1.T * D1
        S2 = D1.T * D2
        S3 = D2.T * D2

        # Constraint matrix [eqn. 18]
        C1 = np.mat('0. 0. 2.; 0. -1. 0.; 2. 0. 0.')

        # Reduced scatter matrix [eqn. 29]
        M = C1.I * (S1 - S2 * S3.I * S2.T)

        # M*|a b c >=l|a b c >. Find eigenvalues and eigenvectors from this equation [eqn. 28]
        eval, evec = np.linalg.eig(M)

        # eigenvector must meet constraint 4ac - b^2 to be valid.
        cond = 4 * np.multiply(evec[0, :], evec[2, :]) - np.power(evec[1, :], 2)
        a1 = evec[:, np.nonzero(cond.A > 0)[1]]

        # |d f g> = -S3^(-1)*S2^(T)*|a b c> [eqn. 24]
        a2 = -S3.I * S2.T * a1

        # eigenvectors |a b c d f g>
        self.coef = np.vstack([a1, a2])
        self._save_parameters()

    def _save_parameters(self):
        """finds the important parameters of the fitted ellipse

        Theory taken form http://mathworld.wolfram
        Args
        -----
        coef (list): list of the coefficients describing an ellipse
           [a,b,c,d,f,g] corresponding to ax**2+2bxy+cy**2+2dx+2fy+g
        Returns
        _______
        center (List): of the form [x0, y0]
        width (float): major axis
        height (float): minor axis
        phi (float): rotation of major axis form the x-axis in radians
        """

        # eigenvectors are the coefficients of an ellipse in general form
        # a*x^2 + 2*b*x*y + c*y^2 + 2*d*x + 2*f*y + g = 0 [eqn. 15) from (**) or (***)
        a = self.coef[0, 0]
        b = self.coef[1, 0] / 2.
        c = self.coef[2, 0]
        d = self.coef[3, 0] / 2.
        f = self.coef[4, 0] / 2.
        g = self.coef[5, 0]

        # finding center of ellipse [eqn.19 and 20] from (**)
        x0 = (c * d - b * f) / (b ** 2. - a * c)
        y0 = (a * f - b * d) / (b ** 2. - a * c)

        # Find the semi-axes lengths [eqn. 21 and 22] from (**)
        numerator = 2 * (a * f * f + c * d * d + g * b * b - 2 * b * d * f - a * c * g)
        denominator1 = (b * b - a * c) * ((c - a) * np.sqrt(1 + 4 * b * b / ((a - c) * (a - c))) - (c + a))
        denominator2 = (b * b - a * c) * ((a - c) * np.sqrt(1 + 4 * b * b / ((a - c) * (a - c))) - (c + a))
        width = np.sqrt(numerator / denominator1)
        height = np.sqrt(numerator / denominator2)

        # angle of counterclockwise rotation of major-axis of ellipse to x-axis [eqn. 23] from (**)
        # or [eqn. 26] from (***).
        phi = .5 * np.arctan((2. * b) / (a - c))

        self._center = [x0, y0]
        self._width = width
        self._height = height
        self._phi = phi

    @property
    def center(self):
        return self._center

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def phi(self):
        """angle of counterclockwise rotation of major-axis of ellipse to x-axis
        [eqn. 23] from (**)
        """
        return self._phi

    def parameters(self):
        return self.center, self.width, self.height, self.phi


def make_test_ellipse(center=[1, 1], width=1, height=.6, phi=3.14 / 5):
    """Generate Elliptical data with noise
    Args
    ----
    center (list:float): (<x_location>, <y_location>)
    width (float): semimajor axis. Horizontal dimension of the ellipse (**)
    height (float): semiminor axis. Vertical dimension of the ellipse (**)
    phi (float:radians): tilt of the ellipse, the angle the semimajor axis
        makes with the x-axis
    Returns
    -------
    data (list:list:float): list of two lists containing the x and y data of the
        ellipse. of the form [[x1, x2, ..., xi],[y1, y2, ..., yi]]
    """
    t = np.linspace(0, 2 * np.pi, 1000)
    x_noise, y_noise = np.random.rand(2, len(t))

    ellipse_x = center[0] + width * np.cos(t) * np.cos(phi) - height * np.sin(t) * np.sin(
        phi) + x_noise / 2.
    ellipse_y = center[1] + width * np.cos(t) * np.sin(phi) + height * np.sin(t) * np.cos(
        phi) + y_noise / 2.

    return [ellipse_x, ellipse_y]



def random_color(ite=1):#Create a random color
        cols=[]
        for replicate in range(ite):
            levels = range(32, 256, 32)
            levels = str(tuple(random.choice(levels) for _ in range(3)))
            cols.append(tuple(int(s) for s in levels.strip("()").split(",")))
        return (cols)


def smooth_coos(Coos, window_length, polyorder):
    #Apply a smoothing filter
    for ind in range(len(Coos)):
        ind_coo=[[np.nan if val==-1000 else val for val in row ] for row in Coos[ind]]
        ind_coo=np.array(ind_coo, dtype=np.float)
        for column in range(2):
            Pos_NA = np.where(np.isnan(ind_coo[:, column]))[0]
            debuts = [0]
            fins = []
            if len(Pos_NA) > 0:
                diff = ([Pos_NA[ele] - Pos_NA[ele - 1] for ele in range(1, len(Pos_NA))])
                fins.append(Pos_NA[0])
                for moment in range(len(diff)):
                    if diff[moment] > 1:
                        fins.append(Pos_NA[moment + 1])
                        debuts.append(Pos_NA[moment])
                debuts.append(Pos_NA[len(Pos_NA) - 1])
                fins.append(len(ind_coo[:, column]))

                for seq in range(len(debuts)):
                    if len(ind_coo[(debuts[seq] + 1):fins[seq], column]) >= window_length:
                        ind_coo[(debuts[seq] + 1):fins[seq], column] = savgol_filter(
                            ind_coo[(debuts[seq] + 1):fins[seq], column], window_length,
                            polyorder, deriv=0, delta=1.0, axis=- 1,
                            mode='interp', cval=0.0)
            else:
                ind_coo[:, column] = savgol_filter(ind_coo[:, column],
                                                                   window_length,
                                                                   polyorder, deriv=0, delta=1.0, axis=- 1,
                                                                   mode='interp', cval=0.0)
        ind_coo = ind_coo.astype(np.str)
        ind_coo[np.where(ind_coo == "nan")] = -1000
        ind_coo = ind_coo.astype(dtype=float)
        Coos[ind] = ind_coo
    return(Coos)