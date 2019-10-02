import io

import base64

import cv2
import imutils
import numpy as np

class LaneRecognition:

    @classmethod
    def detect_edges(cls, frame):
        # filter for blue lane lines
        cv2.imwrite('images/processed/{}_real.jpg'.format(image_name), frame)

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        cv2.imwrite('images/processed/{}_cvt.jpg'.format(image_name), hsv)
        blur_image = cv2.GaussianBlur(hsv, (7, 7), 7)
        # cv2.imwrite('images/processed/{}_blur_image.jpg'.format(image_name), blur_image)
        #gray_image = cv2.cvtColor(blur_image, cv2.COLOR_BGR2GRAY)
        lower_blue = np.array([0, 40, 40])
        upper_blue = np.array([150, 255, 255])
        mask = cv2.inRange(blur_image, lower_blue, upper_blue)
        cv2.imwrite('images/processed/{}_color_mask.jpg'.format(image_name), mask)

        # detect edges
        edges = cv2.Canny(mask, 75, 200)
        edges = cv2.dilate(edges, np.ones((3, 3)))
        cv2.imwrite('images/processed/{}_canny.jpg'.format(image_name), edges)

        # value = 350  # this is for (1820, 960) resolution
        # value = 450  # this is for (1640, 1232) resolution
        # value = 900  # this is for (3280, 2464) resolution
        value = 100  # this is for (375, 500) resolution

        imshape = edges.shape
        #Here we define the area of interest
        lower_left = [0, imshape[0]]
        lower_left_mid = [0, imshape[0]-value]
        lower_right = [imshape[1], imshape[0]]
        lower_right_mid = [imshape[1], imshape[0]-value]
        top_left = [imshape[1]/2-imshape[1]/10, imshape[0]/3+imshape[0]/10]
        top_right = [imshape[1]/2+imshape[1]/10, imshape[0]/3+imshape[0]/10]
        vertices = [np.array([lower_left, lower_left_mid, top_left, top_right, lower_right_mid, lower_right],
                             dtype=np.int32)]

        roi_image = cls.region_of_interest(edges, vertices)
        cv2.imwrite('images/processed/{}_roi.jpg'.format(image_name), roi_image)

        return roi_image

    @classmethod
    def region_of_interest(cls, img, vertices):
        # defining a blank mask to start with
        mask = np.zeros_like(img)

        # defining a 3 channel or 1 channel color to fill the mask with depending on the input image
        if len(img.shape) > 2:
            channel_count = img.shape[2]  # i.e. 3 or 4 depending on your image
            ignore_mask_color = (255,) * channel_count
        else:
            ignore_mask_color = 255
        # filling pixels inside the polygon defined by "vertices" with the fill color
        cv2.fillPoly(mask, vertices, ignore_mask_color)

        # cv2.polylines(img, vertices, True, (255, 0, 0), 3) # this is used to drow ROI on the image.

        # returning the image only where mask pixels are nonzero
        masked_image = cv2.bitwise_and(img, mask)
        return masked_image

    @classmethod
    def detect_line_segments(cls, cropped_edges):
        # tuning min_threshold, minLineLength, maxLineGap is a trial and error process by hand
        rho = 1  # distance precision in pixel, i.e. 1 pixel
        angle = np.pi / 180  # angular precision in radian, i.e. 1 degree
        min_threshold = 10  # minimal of votes
        line_segments = cv2.HoughLinesP(cropped_edges, rho, angle, min_threshold,
                                        np.array([]), minLineLength=8, maxLineGap=4)

        return line_segments

    @classmethod
    def make_points(cls, frame, line):
        height, width, _ = frame.shape
        slope, intercept = line
        y1 = height  # bottom of the frame
        y2 = int(y1 * 1 / 2)  # make points from middle of the frame down

        # bound the coordinates within the frame
        x1 = max(-width, min(2 * width, int((y1 - intercept) / slope)))
        x2 = max(-width, min(2 * width, int((y2 - intercept) / slope)))
        return [[x1, y1, x2, y2]]

    @classmethod
    def average_slope_intercept(cls, frame, line_segments):
        """
        This function combines line segments into one or two lane lines
        If all line slopes are < 0: then we only have detected left lane
        If all line slopes are > 0: then we only have detected right lane
        """
        lane_lines = []
        if line_segments is None:
            return lane_lines

        height, width, _ = frame.shape
        left_fit = []
        right_fit = []

        boundary = 1/3
        left_region_boundary = width * (1 - boundary)  # left lane line segment should be on left 2/3 of the screen
        right_region_boundary = width * boundary # right lane line segment should be on left 2/3 of the screen

        for line_segment in line_segments:
            for x1, y1, x2, y2 in line_segment:
                if x1 == x2:
                    continue
                fit = np.polyfit((x1, x2), (y1, y2), 1)
                slope = fit[0]
                intercept = fit[1]
                if slope < 0:
                    if x1 < left_region_boundary and x2 < left_region_boundary:
                        left_fit.append((slope, intercept))
                else:
                    if x1 > right_region_boundary and x2 > right_region_boundary:
                        right_fit.append((slope, intercept))

        left_fit_average = np.average(left_fit, axis=0)
        if len(left_fit) > 0:
            lane_lines.append(cls.make_points(frame, left_fit_average))

        right_fit_average = np.average(right_fit, axis=0)
        if len(right_fit) > 0:
            lane_lines.append(cls.make_points(frame, right_fit_average))

        return lane_lines

    @classmethod
    def display_lines(cls, frame, lines, line_color=(0, 255, 0), line_width=2):
        line_image = np.zeros_like(frame)
        if lines is not None:
            for line in lines:
                for x1, y1, x2, y2 in line:
                    cv2.line(line_image, (x1, y1), (x2, y2), line_color, line_width)
        line_image = cv2.addWeighted(frame, 0.8, line_image, 1, 1)
        return line_image

    @classmethod
    def display_heading_line(cls, frame, steering_angle, line_color=(0, 0, 255), line_width=5 ):
        heading_image = np.zeros_like(frame)
        height, width, _ = frame.shape

        # figure out the heading line from steering angle
        # heading line (x1,y1) is always center bottom of the screen
        # (x2, y2) requires a bit of trigonometry

        # Note: the steering angle of:
        # 0-89 degree: turn left
        # 90 degree: going straight
        # 91-180 degree: turn right
        steering_angle_radian = steering_angle / 180.0 * np.math.pi
        x1 = int(width / 2)
        y1 = height
        x2 = int(x1 - height / 2 / np.math.tan(steering_angle_radian))
        y2 = int(height / 2)

        cv2.line(heading_image, (x1, y1), (x2, y2), line_color, line_width)
        heading_image = cv2.addWeighted(frame, 0.8, heading_image, 1, 1)

        return heading_image

    @classmethod
    def detect_lane(cls, frame):
        edges = cls.detect_edges(frame)
        cv2.imwrite('images/processed/{}_cropped_edges.jpg'.format(image_name), edges)
        line_segments = cls.detect_line_segments(edges)
        lane_lines = cls.average_slope_intercept(frame, line_segments)

        return lane_lines

    @classmethod
    def process_image(cls, frame):
        frame = imutils.resize(frame, 500)
        lane_lines = cls.detect_lane(frame)
        line_image = cls.display_lines(frame, lane_lines)
        cv2.imwrite('images/processed/{}_lines.jpg'.format(image_name), line_image)
        if len(lane_lines) > 1:
            _, _, left_x2, _ = lane_lines[0][0]
            _, _, right_x2, _ = lane_lines[1][0]
            mid = int(frame.shape[1] / 2)
            x_offset = (left_x2 + right_x2) / 2 - mid
            y_offset = int(frame.shape[0] / 2)
        elif len(lane_lines) == 1:
            x1, _, x2, _ = lane_lines[0][0]
            x_offset = x2 - x1
            y_offset = int(frame.shape[0] / 2)
        else:
            return 0
        angle_to_mid_radian = np.math.atan(x_offset / y_offset)  # angle (in radian) to center vertical line
        angle_to_mid_deg = int(angle_to_mid_radian * 180.0 / np.math.pi)  # angle (in degrees) to center vertical line
        steering_angle = angle_to_mid_deg + 90  # this is the steering angle needed by picar front wheel

        heading_line = cls.display_heading_line(line_image, steering_angle)
        cv2.imwrite('images/processed/{}_heading_ling.jpg'.format(image_name), heading_line)
        return steering_angle

from PIL import Image
def string_base64_to_image(base64_string):
    imgdata = base64.b64decode(base64_string)
    return cv2.cvtColor(np.array(Image.open(io.BytesIO(imgdata))), cv2.COLOR_RGB2BGR)

def image_to_base64(image):
    retval, buffer = cv2.imencode('.jpg', image)
    jpg_as_text = base64.b64encode(buffer)
    return jpg_as_text.decode("utf-8")



image_name = "image_3"
frame = cv2.imread('{}.jpg'.format(image_name))
string_base64_to_image(image_to_base64(frame))

print(LaneRecognition.process_image(string_base64_to_image(image_to_base64(frame))))
