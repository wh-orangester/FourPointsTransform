#! /usr/bin/env python
#
#	Create date 2017/10/21
#

######################################################
#	Import Standard

import os
import sys

import math

import numpy as np

######################################################
#	Import Local

######################################################
#	Globel Member

######################################################
#	Helper Function

def computeFourPointTransformMatrix( P00, P10, P11, P01 ):
	''' This function will create four-point transform matrix to
		transform 1-by-1 square into quadrilateral
		INPUTS : 4 point as numpy array
		OUTPUT : four-point transform 4-by-4 matrix as numpy array

		WARNING - If you want to use P00 as reference point of transform,
		          do translate all point so that P00 is (0,0)

		Reference : https://en.wikipedia.org/wiki/Transformation_matrix#Perspective_projection
		Reference Image : https://en.wikipedia.org/wiki/Transformation_matrix#/media/File:Perspective_transformation_matrix_2D.svg
	'''

	#   From the reference image if we found g and h,
	#       we can convert quadrilateral into parallelogram
	#       in which we can solve for a, b, c, d, e, f
	#   From figure 4, we have the equations:
	#       P00_x = c ___________________ [eq.1]
	#       P00_y = f ___________________ [eq.2]
	#       P01_x = (b+c)/(h+1) _________ [eq.3]
	#       P01_y = (e+f)/(h+1) _________ [eq.4]
	#       P11_x = (a+b+c)/(g+h+1) _____ [eq.5]
	#       P11_y = (d+e+f)/(g+h+1) _____ [eq.6]
	#       P10_x = (a+c)/(g+1) _________ [eq.7]
	#       P10_y = (d+f)/(g+1) _________ [eq.8]
	#   NOTES that all value on lhs of above equations are representing
	#       point on given quadrilateral

	#   Assume h+1 != 0 and g+1 != 0 and g+h+1 != 0
	#       (If this case even occurred, we should get quadrilateral with
	#       some point go toward infinity by now. So just ignore it)
	#   We get:
	#       P01_x*(h+1) = b+c ___________ [eq.9] from [eq.3]
	#       P01_y*(h+1) = e+f ___________ [eq.10] from [eq.4]
	#       P11_x*(g+h+1) = a+b+c _______ [eq.11] from [eq.5]
	#       P11_y*(g+h+1) = d+e+f _______ [eq.12] from [eq.6]
	#       P10_x*(g+1) = a+c ___________ [eq.13] from [eq.7]
	#       P10_y*(g+1) = d+f ___________ [eq.14] from [eq.8]
	#   Combine equations and we get:
	#       P11_x*(g+h+1) - P01_x*(h+1) - P10_x*(g+1) + P00_x = 0 [eq.15] from [eq.1,9,11,13]
	#       P11_y*(g+h+1) - P01_y*(h+1) - P10_y*(g+1) + P00_y = 0 [eq.16] from [eq.2,10,12,14]
	#   Rearrage the equations:
	#       (P11_x-P10_x)*g + (P11_x-P01_x)*h = P01_x + P10_x - P11_x - P00_x [eq.17] from [eq.15]
	#       (P11_y-P10_y)*g + (P11_y-P01_y)*h = P01_y + P10_y - P11_y - P00_y [eq.18] from [eq.16]

	#
	#   The following section will solve for g and h
	#       using [eq.15,16]
	#

	#   compute coefficient in the equation
	t0 = P11 - P10
	t1 = P11 - P01
	t2 = P01 + P10 - P11 - P00

	#   now we get:
	#       t0_x*g + t1_x*h = t2_x
	#       t0_y*g + t1_y*h = t2_y
	#   arrange into matrix:
	#       [[t0_x,t1_x],[t0_y,t1_y]] * [[g],[h]] = [[t2_x],[t2_y]]
	#       [[g],[h]] = [[t0_x,t1_x],[t0_y,t1_y]]^-1 * [[t2_x],[t2_y]]

	#	try to compute for g and h
	try:
		result = np.matrix( [ [ t0[0], t1[0] ], [ t0[1], t1[1] ] ] ).I * np.matrix( [ [ t2[0], t2[1] ] ] ).T
	except np.linalg.LinAlgError:
		#	NOTES - this exception caused by trying to invert non-invertible matrix
		#			this will occur when eq.15 and eq.16 is not independent
		#			(eq.15 can be multiply by some constant to get eq.16)
		#			Such a case happen when both section P11-P10 and P11-P01
		#			are aligned as single line
		print "Cannot solve for because P00-P01 and P00-P10 are parallel"

	#   destructure result vector into g and h
	g, h = [ result[i,0] for i in (0,1) ]

	#	assert that g, h stay in valid domain
	assert( g != -1 )
	assert( h != -1 )
	assert( g + h != -1)

	#
	#   The following section will compute parallelogram's points
	#       as in figure 1 and 4 of reference image
	#   NOTES that parallelogram's position is defined by [eq.9,10,11,12,13,14]
	#   ALSO NOTES that from here on we will refer to parallelogram points
	#       by add subfix *_prime to variable while quadrilateral has no suffix:
	#       P00_prime_x = P00_x _______________________ [eq.19] from [eq.1]
	#       P00_prime_y = P00_y _______________________ [eq.20] from [eq.2]
	#       P01_prime_x = P01_x*(h+1) = b+c ___________ [eq.21] from [eq.9]
	#       P01_prime_y = P01_y*(h+1) = e+f ___________ [eq.22] from [eq.10]
	#       P11_prime_x = P11_x*(g+h+1) = a+b+c _______ [eq.23] from [eq.11]
	#       P11_prime_y = P11_y*(g+h+1) = d+e+f _______ [eq.24] from [eq.12]
	#       P10_prime_x = P10_x*(g+1) = a+c ___________ [eq.25] from [eq.13]
	#       P10_prime_y = P10_y*(g+1) = d+f ___________ [eq.24] from [eq.14]
	#

	#   compute parallelogram's points
	P00_prime = np.array( P00 )
	P01_prime = np.array( P01 ) * ( h + 1 )
	P11_prime = np.array( P11 ) * ( g + h + 1 )
	P10_prime = np.array( P10 ) * ( g + 1 )

	#   assert that the given parallelogram points
	#       really form  aparallelogram by check parallelity of 2 opposite segment pairs
	assert( P01_prime[0] - P00_prime[0] - P11_prime[0] + P10_prime[0] <= 1e-6 )
	assert( P01_prime[1] - P00_prime[1] - P11_prime[1] + P10_prime[1] <= 1e-6 )
	assert( P10_prime[0] - P00_prime[0] - P11_prime[0] + P01_prime[0] <= 1e-6 )
	assert( P10_prime[1] - P00_prime[1] - P11_prime[1] + P01_prime[1] <= 1e-6 )

	#
	#   The following section compute for a, b, c, d, e, f
	#       and construct numpy array as matrix of
	#       four-point transform and return

	#   compute a, b, c, d, e, f
	a = P10_prime[0] - P00_prime[0]
	b = P01_prime[0] - P00_prime[0]
	c = P00_prime[0]
	d = P10_prime[1] - P00_prime[1]
	e = P01_prime[1] - P00_prime[1]
	f = P00_prime[1]

	#   return
	return np.matrix( [
		[ a, b, 0, c ],
		[ d, e, 0, f ],
		[ 0, 0, 1, 0 ],
		[ g, h, 0, 1 ]
	] )

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

		self.fourPointTransform = computeFourPointTransformMatrix( \
										np.array( [ p0.x, p0.y ] ), \
										np.array( [ p1.x, p1.y ] ), \
										np.array( [ p2.x, p2.y ] ), \
										np.array( [ p3.x, p3.y ] ) )

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

		#   transform by matrix
		transformedPoint = self.fourPointTransform.I * np.matrix( [[ x, y, 0, 1 ]] ).T

		#   return
		return transformedPoint[0,0] / transformedPoint[3,0], transformedPoint[1,0] / transformedPoint[3,0]

	def calculateXYFromUV( self, u, v ):
		'''	this function will calculate xy in four corner point used bilinear interpolation
		'''

		#   transform by matrix
		transformedPoint = self.fourPointTransform * np.matrix( [[ u, v, 0, 1 ]] ).T

		#   return
		return transformedPoint[0,0] / transformedPoint[3,0], transformedPoint[1,0] / transformedPoint[3,0]

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
