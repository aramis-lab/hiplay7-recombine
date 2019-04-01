from soma import aims
import sys

inputVolume = aims.read( sys.argv[1] )
bloc_size = int(sys.argv[2])
bloc_position = sys.argv[3]
axis = sys.argv[4]


inputSizeX = inputVolume.getSizeX()
inputSizeY = inputVolume.getSizeY()
inputSizeZ = inputVolume.getSizeZ()
inputResolution = inputVolume.header()[ 'voxel_size' ]
print inputResolution


if( axis == "x" ):
  print "inserting an empty bloc on x for ", bloc_size, " voxels"
  outputSizeX = inputSizeX + bloc_size
  outputSizeY = inputSizeY
  outputSizeZ = inputSizeZ
  outputResolution = inputResolution
  outputVolume = aims.Volume_FLOAT( outputSizeX, outputSizeY, outputSizeZ )
  outputVolume.header().update( inputVolume.header() )
 
  if(bloc_position=='at_end'):  
    for z in xrange( inputSizeZ ):
      for y in xrange( inputSizeY ):
    	for x in xrange( inputSizeX ):
    	   inputVolume.setValue( float(inputVolume.value( x, y, z )), 
    				 x, 
    				 y, 
    				 z )
    for z in xrange( inputSizeZ ):
      for y in xrange( inputSizeY ):
    	for x in xrange( inputSizeX, outputSizeX, 1 ):
    	   inputVolume.setValue( 0.0, 
    				 x, 
    				 y, 
    				 z )

  if(bloc_position=='at_beginning'):  
    for z in xrange( inputSizeZ ):
      for y in xrange( inputSizeY ):
    	for x in xrange( bloc_size ):
    	   inputVolume.setValue( 0.0, 
    				 x, 
    				 y, 
    				 z )
    for z in xrange( inputSizeZ ):
      for y in xrange( inputSizeY ):
    	for x in xrange( bloc_size, outputSizeX, 1 ):
    	   inputVolume.setValue( float(inputVolume.value( x - bloc_size, y, z )), 
    				 x, 
    				 y, 
    				 z )


if( axis == "y" ):
  print "inserting an empty bloc on y for ", bloc_size, " voxels"
  outputSizeX = inputSizeX
  outputSizeY = inputSizeY + bloc_size
  outputSizeZ = inputSizeZ
  outputResolution = inputResolution
  outputVolume = aims.Volume_FLOAT( outputSizeX, outputSizeY, outputSizeZ )
  outputVolume.header().update( inputVolume.header() )

  if(bloc_position=='at_end'):  
    for z in xrange( inputSizeZ ):
      for y in xrange( inputSizeY ):
    	for x in xrange( inputSizeX ):
    	   outputVolume.setValue( float(inputVolume.value( x, y, z )), 
    				  x, 
    				  y, 
    				  z )
    for z in xrange( inputSizeZ ):
      for y in xrange( inputSizeY, outputSizeY, 1 ):
    	for x in xrange( inputSizeX ):
    	   outputVolume.setValue( 0.0, 
    				  x, 
    				  y, 
    				  z )

  if(bloc_position=='at_beginning'):  
    for z in xrange( inputSizeZ ):
      for y in xrange( bloc_size ):
    	for x in xrange( inputSizeX ):
    	   outputVolume.setValue( 0.0, 
    				  x, 
    				  y, 
    				  z )
    for z in xrange( inputSizeZ ):
      for y in xrange( bloc_size, outputSizeY, 1 ):
    	for x in xrange( inputSizeX ):
    	   outputVolume.setValue( float(inputVolume.value( x, y - bloc_size, z )), 
    				  x, 
    				  y, 
    				  z )


if( axis == "z" ):
  print "inserting an empty bloc on z for ", bloc_size, " voxels"
  outputSizeX = inputSizeX
  outputSizeY = inputSizeY
  outputSizeZ = inputSizeZ + bloc_size
  outputResolution = inputResolution
  outputVolume = aims.Volume_FLOAT( outputSizeX, outputSizeY, outputSizeZ )
  outputVolume.header().update( inputVolume.header() )

  if(bloc_position=='at_end'):  
    for z in xrange( inputSizeZ ):
      for y in xrange( inputSizeY ):
    	for x in xrange( inputSizeX ):
    	   outputVolume.setValue( float(inputVolume.value( x, y, z )), 
    				  x, 
    				  y, 
    				  z )
    for z in xrange( inputSizeZ, outputSizeZ, 1 ):
      for y in xrange( inputSizeY ):
    	for x in xrange( inputSizeX ):
    	   outputVolume.setValue( 0.0, 
    				  x,
    				  y,
    				  z )		  

  if(bloc_position=='at_beginning'):  
    for z in xrange( bloc_size ):
      for y in xrange( inputSizeY ):
    	for x in xrange( inputSizeX ):
    	   outputVolume.setValue( 0.0,
    				  x,
    				  y,
    				  z )
    for z in xrange( bloc_size, outputSizeZ, 1 ):
      for y in xrange( inputSizeY ):
    	for x in xrange( inputSizeX ):
    	   outputVolume.setValue( float(inputVolume.value( x, y, z - bloc_size)),
    				  x, 
    				  y, 
    				  z )
				  
aims.write( outputVolume, sys.argv[5], options={ 'force_disk_data_type' : True } )





