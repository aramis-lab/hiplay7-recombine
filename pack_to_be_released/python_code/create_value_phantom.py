from soma import aims
import sys

inputVolume = aims.read( sys.argv[1] )
value = float( sys.argv[2] )

inputSizeX = inputVolume.getSizeX()
inputSizeY = inputVolume.getSizeY()
inputSizeZ = inputVolume.getSizeZ()
#inputTransformations = inputVolume.header()[ 'transformations' ]
#inputResolution = inputVolume.header()[ 'voxel_size' ]
#storageToMemory = inputVolume.header()[ 'storage_to_memory' ]

outputVolume = aims.Volume_FLOAT( inputSizeX, inputSizeY, inputSizeZ )
outputVolume.header().update( inputVolume.header() )
#outputVolume.header()[ 'voxel_size' ] = inputResolution
#outputVolume.header()[ 'storage_to_memory' ] = storageToMemory
#outputVolume.header()[ 'transformations' ] = inputTransformations


print "filling volume with the value: ", value
for z in xrange( inputSizeZ ):
  for y in xrange( inputSizeY ):
    for x in xrange( inputSizeX ):
      outputVolume.setValue( value, x, y, z )

#gradient = value / inputSizeX
#for x in xrange( inputSizeX ):
#  outputVolume.setValue( x * gradient, x, 0, 0 )
#  outputVolume.setValue( x * gradient, x, 1, 0 )


aims.write( outputVolume, sys.argv[3], options={ 'force_disk_data_type' : True } )
