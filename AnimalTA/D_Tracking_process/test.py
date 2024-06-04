import cv2
import numpy as np

# Create a Kalman Filter
kalman = cv2.KalmanFilter(4, 2)
kalman.measurementMatrix = np.array([[1, 0, 0, 0],
                                     [0, 1, 0, 0]], np.float32)
kalman.transitionMatrix = np.array([[1, 0, 1, 0],
                                    [0, 1, 0, 1],
                                    [0, 0, 1, 0],
                                    [0, 0, 0, 1]], np.float32)
kalman.processNoiseCov = np.eye(4, dtype=np.float32) * 0.00001

# Initialize state and measurement vectors
state = np.zeros((4, 1), np.float32)
measurement = np.zeros((2, 1), np.float32)

# Mouse callback function
def mouse_move(event, x, y, flags, param):
    global measurement
    measurement = np.array([[np.float32(x)], [np.float32(y)]])

# Create a window and set mouse callback
cv2.namedWindow("Kalman Filter")
cv2.setMouseCallback("Kalman Filter", mouse_move)

while True:
    # Predict the next state
    prediction = kalman.predict()
    pred_x, pred_y = int(prediction[0]), int(prediction[1])

    # Correct the prediction based on the measurement
    kalman.correct(measurement)

    # Get the measured position
    meas_x, meas_y = int(measurement[0]), int(measurement[1])

    # Create an empty image
    frame = np.zeros((500, 500, 3), dtype=np.uint8)

    # Draw the measured position
    cv2.circle(frame, (meas_x, meas_y), 5, (0, 255, 0), -1)

    # Draw the predicted position
    cv2.circle(frame, (pred_x, pred_y), 5, (0, 0, 255), -1)

    # Display the image
    cv2.imshow("Kalman Filter", frame)

    # Break the loop on ESC key press
    if cv2.waitKey(1) & 0xFF == 27:
        break

cv2.destroyAllWindows()