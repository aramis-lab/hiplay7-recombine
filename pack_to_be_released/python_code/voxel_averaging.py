from soma import aims
import sys

inputVolume = aims.read( sys.argv[1] )
averaging_factor = int( sys.argv[2] )
axis = sys.argv[3]

inputSizeX = inputVolume.getSizeX()
inputSizeY = inputVolume.getSizeY()
inputSizeZ = inputVolume.getSizeZ()
inputResolution = inputVolume.header()[ 'voxel_size' ]

print inputResolution
print inputSizeX
print inputSizeY
print inputSizeZ

outputSizeX = inputSizeX
outputSizeY = inputSizeY
outputSizeZ = inputSizeZ
outputResolution = inputResolution

if( axis == "x" ):
  if ( inputSizeX % averaging_factor != 0 ):
    print "wrong averaging factor, sizeX must be multiple of factor"
  else:
    outputSizeX = inputSizeX / averaging_factor
    outputResolution[0] = inputResolution[0] * averaging_factor
        
if( axis == "y" ):
  if ( inputSizeY % averaging_factor != 0 ):
    print "wrong averaging factor, sizeY must be multiple of factor"
  else:
    outputSizeY = inputSizeY / averaging_factor
    outputResolution[1] = inputResolution[1] * averaging_factor
    
if( axis == "z" ):
  if ( inputSizeZ % averaging_factor != 0 ):
    print "wrong averaging factor, sizeZ must be multiple of factor"
  else:
    outputSizeZ = inputSizeZ / averaging_factor
    outputResolution[2] = inputResolution[2] * averaging_factor


outputVolume = aims.Volume_S16( outputSizeX, outputSizeY, outputSizeZ )
outputVolume.header().update( inputVolume.header() )
outputVolume.header()[ 'volume_dimension' ] = [ outputSizeX, 
                                              outputSizeY, 
					      outputSizeZ ]

outputVolume.header()[ 'voxel_size' ] = outputResolution

if( axis == "x" ):
  print "averaging along x with a factor: ", averaging_factor
  for z in xrange( outputSizeZ ):
    for y in xrange( outputSizeY ):
      for x in xrange( outputSizeX ):
        newValue = 0
	for i in xrange( averaging_factor ):
	  newValue += inputVolume.value( averaging_factor * x + i, y, z )
	newValue /= averaging_factor
        outputVolume.setValue( newValue, x, y, z )
        
if( axis == "y" ):
  print "averaging along y with a factor: ", averaging_factor
  for z in xrange( outputSizeZ ):
    for x in xrange( outputSizeX ):
      for y in xrange( outputSizeY ):
        newValue = 0
	for i in xrange( averaging_factor ):
	  newValue += inputVolume.value( x, averaging_factor * y + i, z )
	newValue /= averaging_factor
        outputVolume.setValue( newValue, x, y, z )
        
if( axis == "z" ):
  print "averaging along z with a factor: ", averaging_factor
  for x in xrange( outputSizeX ):
    for y in xrange( outputSizeY ):
      for z in xrange( outputSizeZ ):
        newValue = 0
	for i in xrange( averaging_factor ):
	  newValue += inputVolume.value( x, y, averaging_factor * z + i )
	newValue /= averaging_factor
        outputVolume.setValue( newValue, x, y, z )
	
aims.write( outputVolume, sys.argv[4] )

print outputResolution
print outputSizeX
print outputSizeY
print outputSizeZ
