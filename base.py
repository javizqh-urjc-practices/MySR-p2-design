import pybullet as p
import pybullet_data
import argparse
import time


parser = argparse.ArgumentParser(description="URDF viewer example")
parser.add_argument("--urdf", type=str, required=True, help="Ruta al archivo URDF.")
args = parser.parse_args()
urdf_path = args.urdf

physicsClient = p.connect(p.GUI) #or p.DIRECT for non-graphical version
p.setAdditionalSearchPath(pybullet_data.getDataPath()) #optionally
p.setGravity(0,0,-9.8)

planeId = p.loadURDF("plane_transparent.urdf")

startPos = [0,0,1]
startOrientation = p.getQuaternionFromEuler([0,0,-3.15])

robotId = p.loadURDF(urdf_path,startPos, startOrientation)

#p.setRealTimeSimulation(1)

# Only to know what is the number of the wheels
numJoints = p.getNumJoints(robotId)
print("NumJoints: " + str(numJoints))

for j in range (numJoints):
    print("%d - %s" % (p.getJointInfo(robotId,j)[0], p.getJointInfo(robotId,j)[1].decode("utf-8")))

joints = [0,1,2,3]

try:
    while True:
        p.stepSimulation()
        time.sleep(1./240.)
        speed = 1.5
        torque = 25.0
        
        p.setJointMotorControlArray(robotId, joints, p.VELOCITY_CONTROL, targetVelocities=[speed, speed, speed, speed], forces=[torque, torque, torque, torque])
            
except KeyboardInterrupt:
      pass
	
p.disconnect()    
