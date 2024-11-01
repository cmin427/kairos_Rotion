import numpy as np
import matplotlib.pyplot as plt

# 주어진 중심값과 로봇팔 좌표값 데이터
center_points = np.array([
    [357, 116], [323,116], [272, 123], [235, 118], [354, 130], 
    [287, 125], [191, 111], [329, 124], [354, 123],
    [290, 121], [295, 118], [287, 117], [321, 120]
])
robot_positions = np.array([
    [-88, -209], [-78, -209], [-51, -209], [-38, -209], [-88, -200], 
    [-58, -200], [-17, -209], [-76, -205], [-87, -205],
    [-59, -204], [-62, -205], [-57, -209], [-71, -209]
])

# 보간 계수 계산
coeff_x = np.polyfit(center_points[:, 0], robot_positions[:, 0], 1)
coeff_y = np.polyfit(center_points[:, 1], robot_positions[:, 1], 1)

# 중심값에 따른 예상 로봇팔 좌표값 계산
predicted_robot_x = np.polyval(coeff_x, center_points[:, 0])
predicted_robot_y = np.polyval(coeff_y, center_points[:, 1])

# 그래프 시각화
plt.figure(figsize=(14, 6))

# robot_x에 대한 그래프
plt.subplot(1, 2, 1)
plt.scatter(center_points[:, 0], robot_positions[:, 0], color='blue', label='Original robot_x')
plt.plot(center_points[:, 0], predicted_robot_x, color='red', linestyle='--', label='Fitted Line (robot_x)')
plt.xlabel('Center X')
plt.ylabel('Robot X')
plt.title('Center X vs. Robot X')
plt.legend()

# robot_y에 대한 그래프
plt.subplot(1, 2, 2)
plt.scatter(center_points[:, 1], robot_positions[:, 1], color='green', label='Original robot_y')
plt.plot(center_points[:, 1], predicted_robot_y, color='purple', linestyle='--', label='Fitted Line (robot_y)')
plt.xlabel('Center Y')
plt.ylabel('Robot Y')
plt.title('Center Y vs. Robot Y')
plt.legend()

plt.tight_layout()
plt.show()
