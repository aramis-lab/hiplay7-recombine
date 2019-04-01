from soma import aims
import sys

inputVolume1 = aims.read( sys.argv[1] )
inputVolume2 = aims.read( sys.argv[2] )

inputVolume2.header().update( inputVolume1.header() )

aims.write( inputVolume2, sys.argv[3], options={ 'force_disk_data_type' : True } )

