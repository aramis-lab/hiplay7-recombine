from soma import aims
import sys

inputVolume1 = aims.read( sys.argv[1] )
inputVolume2 = aims.read( sys.argv[2] )

inputSizeX1 = inputVolume1.getSizeX()
inputSizeY1 = inputVolume1.getSizeY()
inputSizeZ1 = inputVolume1.getSizeZ()
inputResolution1 = inputVolume1.header()[ 'voxel_size' ]
print inputResolution1

inputSizeX2 = inputVolume2.getSizeX()
inputSizeY2 = inputVolume2.getSizeY()
inputSizeZ2 = inputVolume2.getSizeZ()
inputResolution2 = inputVolume2.header()[ 'voxel_size' ]
print inputResolution2

if ( ( inputSizeX1 != inputSizeX2 ) or 
     ( inputSizeY1 != inputSizeY2 ) or
     ( inputSizeZ1 != inputSizeZ2 ) ):
  print "the input volumes must have the same size"
else:
  outputSizeX = inputSizeX1
  outputSizeY = inputSizeY1
  outputSizeZ = inputSizeZ1
  outputVolume = aims.Volume_FLOAT( outputSizeX, outputSizeY, outputSizeZ )
  outputVolume.header().update( inputVolume1.header() )
  for z in xrange( outputSizeZ ):
    for y in xrange( outputSizeY ):
      for x in xrange( outputSizeX ):
        outputVolume.setValue( inputVolume1.value( x, y, z ) + 
	                       inputVolume2.value( x, y, z ) , 
			       x, 
			       y, 
			       z )

aims.write( outputVolume, sys.argv[3] )
