from soma import aims
import sys

inputVolume = aims.read( sys.argv[1] )
gap_factor = int(sys.argv[2])
gap_position = int(sys.argv[3])
axis = sys.argv[4]

if ( gap_position >= gap_factor):
  print "gap position (sys.argv[3]) must be lower than gap factor (sys.argv[2])"

inputSizeX = inputVolume.getSizeX()
inputSizeY = inputVolume.getSizeY()
inputSizeZ = inputVolume.getSizeZ()

if (inputVolume.header()['disk_data_type']=='FLOAT'):
  value = 0.0
else:
  value = 0

if( axis == "x" ):
  print "inserting a gap on x for 1 voxel over", gap_factor
  for z in xrange( inputSizeZ ):
    for y in xrange( inputSizeY ):
      for x in xrange( inputSizeX ):
        if( x % gap_factor == 0 ):
	  inputVolume.setValue( value, 
	                        x + gap_position, 
				y, 
				z )
	  
if( axis == "y" ):
  print "inserting a gap on y for 1 voxel over", gap_factor
  for z in xrange( inputSizeZ ):
    for x in xrange( inputSizeX ):
      for y in xrange( inputSizeY ):
        if( y % gap_factor == 0 ):
	  inputVolume.setValue( value, 
	                        x, 
				y + gap_position, 
				z )
	  
	  
if( axis == "z" ):
  print "inserting a gap on z for 1 voxel over", gap_factor
  for x in xrange( inputSizeX ):
    for y in xrange( inputSizeY ):
      for z in xrange( inputSizeZ ):
        if( z % gap_factor == 0 ):
	  inputVolume.setValue( value, 
	                        x, 
				y, 
				z + gap_position )
	  				 
    
aims.write( inputVolume, sys.argv[5], options={ 'force_disk_data_type' : True }  )

