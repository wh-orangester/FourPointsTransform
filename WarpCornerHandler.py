#! /usr/bin/env python
#
#	Sumeta (Mo) Boonchamoi
#	Create date 2017/10/21
#

######################################################
#	Import Standard

import os
import sys

import math

######################################################
#	Import Local

######################################################
#	Globel Member

######################################################
#	Helper Function

######################################################
#	Definition Class

class WarpCornerHandler( object ):
	'''	this class designed for warp corner handler
	'''

	def __init__( self, p0, p1, p2, p3 ):
		'''	initialize class.
		'''

		#
		#	Set variable from arguments
		#

		#	store four corner point to member class
		self.p0 = p0
		self.p1 = p1
		self.p2 = p2
		self.p3 = p3

	#
	#	Operation Function
	#

	def calculateUVFromXY( self, x, y ):
		'''	this function will calculate uv in four corner point used bilinear interpolation
		'''

		return self.calculateUVFromXY( x, y )

	def calculateUVFromXY( self, x, y ):
		'''	this function will calculate uv in four corner point used bilinear interpolation
		'''

		A = ( self.p1.y - self.p0.y ) * ( self.p2.x - self.p3.x ) - ( self.p1.x - self.p0.x ) * ( self.p2.y - self.p3.y )
		B = ( self.p0.y - y ) * ( self.p2.x - self.p3.x ) + ( self.p1.y - self.p0.y ) * ( self.p3.x - x ) - ( self.p0.x - x ) * ( self.p2.y - self.p3.y ) - ( self.p1.x -self.p0.x ) * ( self.p3.y - y )
		C = ( self.p0.y - y ) * ( self.p3.x - x ) - ( self.p0.x - x ) * ( self.p3.y - y )

		if A != 0:
			D = B * B - 4 * A * C
			u = ( -B - D**0.5) / ( 2 * A )
		else:
			u = -C / B

		p1x = self.p0.x + ( self.p1.x - self.p0.x ) * u 
		p1y = self.p0.y + ( self.p1.y - self.p0.y ) * u 

		p2x = self.p3.x + ( self.p2.x - self.p3.x ) * u 
		p2y = self.p3.y + ( self.p2.y - self.p3.y ) * u 

		if ( p2x - p1x ) != 0:
			v = ( x - p1x ) / ( p2x - p1x )
		else:
			v = ( y - p1y ) / ( p2y - p1y )

		return u, v

	def calculateXYFromUV( self, u, v ):
		'''	this function will calculate xy in four corner point used bilinear interpolation
		'''	

		p1x = self.p0.x + ( self.p1.x - self.p0.x ) * u 
		p1y = self.p0.y + ( self.p1.y - self.p0.y ) * u 

		p2x = self.p3.x + ( self.p2.x - self.p3.x ) * u 
		p2y = self.p3.y + ( self.p2.y - self.p3.y ) * u 

		x = p1x + ( p2x - p1x ) * v
		y = p1y + ( p2y - p1y ) * v

		return x, y

######################################################
#	Main Function

if __name__ == '__main__':
	'''	this function for run code
	'''

	class Point( object ):
		'''	this class designed for point
		'''

		def __init__( self, x, y ):
			'''	initialize class.
			'''

			self.x = float( x )
			self.y = float( y )
	
	p0 = Point(  0,  0 )
	p1 = Point( 10,  0 )
	p2 = Point( 10, 10 )
	p3 = Point(  0, 10 )

	warpCornerHandler = WarpCornerHandler( p0, p1, p2, p3 )

	print warpCornerHandler.calculateXYFromUV( 0.5, 0.5 )
	print warpCornerHandler.calculateUVFromXY( 5.0, 5.0 )
