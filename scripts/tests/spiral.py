import numpy as np
from scipy.interpolate import CubicSpline

def generate_spiral(start_point, end_point, num_points):
    t = np.linspace(0, 1, num_points)  # Parameter values

    # Create arrays for x and y coordinates
    x = np.linspace(start_point[0], end_point[0], num_points)
    y = np.linspace(start_point[1], end_point[1], num_points)

    # Perform cubic spline interpolation
    cs = CubicSpline(t, np.stack((x, y)).T, bc_type='clamped')

    # Generate points on the spiral
    spiral_points = cs(t)

    return spiral_points.tolist()

start_point = (0, 0)
end_point = (5, 5)
num_circles = 2.5
rotation_way = 'right'
num_points = 100

spiral_points = generate_spiral(start_point, end_point, num_points)
assert start_point == spiral_points[0]
assert end_point == spiral_points[-1]