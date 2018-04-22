import jpype

jvmPath = jpype.getDefaultJVMPath()
print(jvmPath)
# jvmPath = "C:\\Program Files (x86)\\Java\\jdk1.8.0_151\\jre\\bin\\server\\jvm.dll"

jpype.startJVM(jvmPath)
print('JVM启动')
Polygon = jpype.java.awt.Polygon

