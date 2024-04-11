import time
import csv
import pybullet as p
import pybullet_data


def move_to(rob_id, eof, dest, set_force, set_pos_gain):
    """Moves the arm to the specified position"""
    joint_poses = p.calculateInverseKinematics(rob_id, eof, dest)
    # print(p.getLinkState(rob_id, 3)[0])

    for index, target in enumerate(joint_poses):
        p.setJointMotorControl2(
            bodyIndex=rob_id,
            jointIndex=index,
            controlMode=p.POSITION_CONTROL,
            targetPosition=target,
            targetVelocity=0,
            force=set_force,
            positionGain=set_pos_gain,
            velocityGain=1,
        )

    if is_near(p.getLinkState(rob_id, 3)[0], dest, 0.1):
        return True
    return False


def open_gripper(rob_id, gripper_id):
    """Opens the gripper in order to release an object"""
    p.setJointMotorControlArray(
        rob_id,
        gripper_id,
        p.VELOCITY_CONTROL,
        targetVelocities=[1, -1, -1, 1],
        forces=[5] * 4,
    )


def half_open_gripper(rob_id, gripper_id):
    """Closes the gripper a little in order to approach an object"""
    p.setJointMotorControlArray(
        rob_id, gripper_id, p.POSITION_CONTROL, targetPositions=[2, -2, -2, 2]
    )


def close_gripper(rob_id, gripper_id):
    """Closes the gripper in order to grab an object"""
    p.setJointMotorControlArray(
        rob_id,
        gripper_id,
        p.VELOCITY_CONTROL,
        targetVelocities= [-10, 10, 10, -10],
        forces=[50] * 4,
    )


def store_gripper(rob_id, gripper_id):
    """Makes the gripper go to the stored position"""
    p.setJointMotorControlArray(
        rob_id, gripper_id, p.POSITION_CONTROL, targetPositions=[0] * 4
    )


def is_near(pos, dest, threshold):
    """True if the position is near the destination, False otherwise"""
    return (
        ((pos[0] < dest[0] + threshold) and (pos[0] > dest[0] - threshold))
        and ((pos[1] < dest[1] + threshold) and (pos[1] > dest[1] - threshold))
        and ((pos[2] < dest[2] + threshold) and (pos[2] > dest[2] - threshold))
    )


def calculate_waste(rob_id, n_joints):
    """Calculates the amount of waste of the pick and place"""
    waste = 0

    for joint_index in range(n_joints):
        waste += abs(p.getJointState(rob_id, joint_index)[3])

    return waste


physicsClient = p.connect(p.GUI)  # or p.DIRECT for non-graphical version
p.setAdditionalSearchPath(pybullet_data.getDataPath())  # optionally
p.setGravity(0, 0, -9.8)

planeId = p.loadURDF("plane_transparent.urdf")

startPos = [0, 0, 2]
startOrientation = p.getQuaternionFromEuler([0, 0, 1.57])

robotId = p.loadURDF("Urdf/urdf/robot.urdf", startPos, startOrientation)

startPos = [0, 4, 0.1]
startOrientation = p.getQuaternionFromEuler([0, 0, 0])
cubeId = p.loadURDF("Urdf/cube.urdf", startPos, startOrientation)

# Only to know what is the number of the wheels
numJoints = p.getNumJoints(robotId)
print("NumJoints: " + str(numJoints))

for j in range(numJoints):
    print(
        "%d - %s"
        % (p.getJointInfo(robotId, j)[0], p.getJointInfo(robotId, j)[1].decode("utf-8"))
    )

# joints = [1,2,3,4]

# Solo queremos que la cinemática inversa actue sobre los primeros 3 JOINTS
EOF_INDEX = 3

wheels = [9, 10, 11, 12]
gripper = [4, 5, 6, 7]

MOVE_TARGET = 2.7


i = 0

checkpoints = {
    "start": [0, 4, 1],
    "cube": [0, 4, 0.55],
    "lat_move": [1, 3.1, 3.2],
    "deposit": [0, 2, 2.3],
}

p.resetDebugVisualizerCamera(
    cameraDistance=5, cameraYaw=130, cameraPitch=-40, cameraTargetPosition=[0, 4, 1]
)
state = 0
iterations = 0
total_waste = 0
csv_values = []

try:
    while state < 9:
        p.stepSimulation()
        time.sleep(1.0 / 200.0)
        iterations += 1
        if state == 0:
            # First go to [0,2.8,0]
            p.setJointMotorControlArray(
                robotId,
                wheels,
                p.VELOCITY_CONTROL,
                targetVelocities=[-5] * 4,
                forces=[20] * 4,
            )
            distance = p.getBasePositionAndOrientation(robotId)[0][1]
            if distance >= MOVE_TARGET - 0.05 and distance <= MOVE_TARGET + 0.05:
                state += 1
                print(iterations*0.005)
                p.setJointMotorControlArray(
                    robotId,
                    wheels,
                    p.VELOCITY_CONTROL,
                    targetVelocities=[0] * 4,
                    forces=[100] * 4,
                )

        elif state == 1:
            half_open_gripper(robotId, gripper)

            i += 1
            if i > 50:
                state += 1
                print(iterations*0.005)
                i = 0

        elif state == 2:
            if move_to(robotId, EOF_INDEX, checkpoints["cube"], 100, 0.03):
                state += 1
                print(iterations*0.005)

            # Open the lid
            p.setJointMotorControl2(
                robotId, 8, p.VELOCITY_CONTROL, targetVelocity=2.5, force=15
            )

        elif state == 3:
            close_gripper(robotId, gripper)
            i += 1
            if i > 50:
                state += 1
                print(iterations*0.005)
                i = 0

        elif state == 4:
            if move_to(robotId, EOF_INDEX, checkpoints["lat_move"], 200, 0.03):
                state += 1
                print(iterations*0.005)
            close_gripper(robotId, gripper)

        elif state == 5:
            if move_to(robotId, EOF_INDEX, checkpoints["deposit"], 200, 0.01):
                state += 1
                print(iterations*0.005)
            close_gripper(robotId, gripper)

        elif state == 6:
            # Close the gripper
            open_gripper(robotId, gripper)

            i += 1
            if i > 50:
                state += 1
                print(iterations*0.005)
                i = 0

        elif state == 7:
            if move_to(robotId, EOF_INDEX, checkpoints["lat_move"], 100, 0.01):
                state += 1
                print(iterations*0.005)

        elif state == 8:
            if move_to(robotId, EOF_INDEX, checkpoints["start"], 100, 0.006):
                state += 1
                print(iterations*0.005)
            store_gripper(robotId, gripper)

        if state > 0:
            total_waste += calculate_waste(robotId, 7)
            if iterations % 2 == 1:
                csv_values.append([iterations * 0.005, 7, calculate_waste(robotId, 7)])

except KeyboardInterrupt:
    pass

print(total_waste)
print(iterations * 0.005)

p.disconnect()

with open("Fase3_Javier_Izquierdo.csv", "w", newline="", encoding="utf-8") as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=",")
    csv_writer.writerow(["Tiempo", "NúmeroJoints", "G_parcial"])
    for i in csv_values:
        csv_writer.writerow([i[0], i[1], i[2]])
