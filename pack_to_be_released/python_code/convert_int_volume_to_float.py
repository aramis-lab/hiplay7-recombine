from soma import aims
import sys

inputVolume = aims.read( sys.argv[1] )
inputSizeX = inputVolume.getSizeX()
inputSizeY = inputVolume.getSizeY()
inputSizeZ = inputVolume.getSizeZ()
#inputTransformations = inputVolume.header()[ 'transformations' ]
#inputResolution = inputVolume.header()[ 'voxel_size' ]
#storageToMemory = inputVolume.header()[ 'storage_to_memory' ]

outputVolume = aims.Volume_FLOAT( inputSizeX, inputSizeY, inputSizeZ )
outputVolume.header().update( inputVolume.header() )
#outputVolume.header()[ 'transformations' ] = inputTransformations
#outputVolume.header()[ 'voxel_size' ] = inputResolution
#outputVolume.header()[ 'storage_to_memory' ] = storageToMemory

for z in xrange( inputSizeZ ):
  for y in xrange( inputSizeY ):
    for x in xrange( inputSizeX ):
      outputVolume.setValue( float( inputVolume.value( x, y, z )), x, y, z )

aims.write( outputVolume, sys.argv[2], options={ 'force_disk_data_type' : True } )
