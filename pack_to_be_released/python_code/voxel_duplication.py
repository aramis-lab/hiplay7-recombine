from soma import aims
import sys

inputVolume = aims.read( sys.argv[1] )
duplication_factor = int( sys.argv[2] )
axis = sys.argv[3]

inputSizeX = inputVolume.getSizeX()
inputSizeY = inputVolume.getSizeY()
inputSizeZ = inputVolume.getSizeZ()
inputResolution = inputVolume.header()[ 'voxel_size' ]
#inputTransformations = inputVolume.header()[ 'transformations' ]
#storageToMemory = inputVolume.header()[ 'storage_to_memory' ]

outputSizeX = inputSizeX
outputSizeY = inputSizeY
outputSizeZ = inputSizeZ
outputResolution = inputResolution

if( axis == "x" ):
  outputSizeX = inputSizeX * duplication_factor
  outputResolution[0] = inputResolution[0] / duplication_factor
        
if( axis == "y" ):
  outputSizeY = inputSizeY * duplication_factor
  outputResolution[1] = inputResolution[1] / duplication_factor
    
if( axis == "z" ):
  outputSizeZ = inputSizeZ * duplication_factor
  outputResolution[2] = inputResolution[2] / duplication_factor

outputVolume = aims.Volume_S16( outputSizeX, outputSizeY, outputSizeZ )
outputVolume.header().update( inputVolume.header() )
outputVolume.header()[ 'volume_dimension' ] = [ outputSizeX, 
                                                outputSizeY, 
					        outputSizeZ ]
#outputVolume.header()[ 'storage_to_memory' ] = storageToMemory
#outputVolume.header()[ 'transformations' ] = inputTransformations
outputVolume.header()[ 'voxel_size' ] = outputResolution

if( axis == "x" ):
  print "duplicating voxels along x with a factor: ", duplication_factor
  for z in xrange( inputSizeZ ):
    for y in xrange( inputSizeY ):
      for x in xrange( inputSizeX ):
        value = inputVolume.value( x, y, z )
	for i in xrange( duplication_factor ):
          outputVolume.setValue( value, 
	                         x * duplication_factor + i, 
				 y, 
				 z )
if( axis == "y" ):
  print "duplicating voxels along y with a factor: ", duplication_factor
  for z in xrange( inputSizeZ ):
    for x in xrange( inputSizeX ):
      for y in xrange( inputSizeY ):
        value = inputVolume.value( x, y, z )
	for i in xrange( duplication_factor ):
          outputVolume.setValue( value, 
	                         x, 
				 y * duplication_factor + i, 
				 z )
if( axis == "z" ):
  print "duplicating voxels along z with a factor: ", duplication_factor
  for x in xrange( inputSizeX ):
    for y in xrange( inputSizeY ):
      for z in xrange( inputSizeZ ):
        value = inputVolume.value( x, y, z )
	for i in xrange( duplication_factor ):
          outputVolume.setValue( value, 
	                         x, 
				 y, 
				 z * duplication_factor + i )
				 
				 
aims.write( outputVolume, sys.argv[4] )
				 

