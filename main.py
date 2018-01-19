#! /usr/bin/env python
#
#	Sumeta (Mo) Boonchamoi
#	Create date 2017/10/15
#

######################################################
#	Import Standard

import os
import sys

import math
import optparse

import time

from fltk import *

from OpenGL import GL, GLU

######################################################
#	Import Local

#	Warp Corner Handler
from WarpCornerHandler import WarpCornerHandler

######################################################
#	Globel Member

ModuleDescription = 'This script to test warp four points to four points.'

#	NOTES - ScriptVersion.ProgramVersion.SubprogramVersion
ProgramVersion = '1.0.0'
ProgramName = 'main'

NumberRequireArgument = 0 

NumSamplingU = 20
NumSamplingV = 20

######################################################
#	Helper Function

######################################################
#	Definition Class

class Point( object ):
	'''	this class designed for point
	'''

	def __init__( self, x, y ):
		'''	initialize class.
		'''

		self.x = float( x )
		self.y = float( y )

class PointObject( object ):
	'''	this class designed for point object
	'''

	def __init__( self, x, y ):
		'''	initialize class.
		'''

		self.point    = Point( x, y )

		self.srcPoint = Point( x, y )
		self.dstPoint = Point( x, y )

	def render( self ):
		'''	this function will render point to OpenGL
		'''

		GL.glColor4f( 1.0, 1.0, 1.0, 1.0 )
		GL.glPointSize( 8.0 )

		GL.glBegin( GL.GL_POINTS )
		GL.glVertex2f( self.point.x, self.point.y )
		GL.glEnd()

class PointHandler( object ):
	'''	this class designed for point handler
	'''

	def __init__( self, llx, lly, urx, ury ):
		'''	initialize class.
		'''

		self.llx = llx
		self.lly = lly
		self.urx = urx
		self.ury = ury

		#	create empty list to store point object
		self.pointList        = []

		#	create empty list to store openGL widget
		self.openGLWidgetList = []

	def addPoint( self, pointObject ):
		'''	add point object to list
		'''

		self.pointList.append( pointObject )

	def addOpenGLWidget( self, openGLWidget ):
		'''	add openGL widget to list
		'''	

		self.openGLWidgetList.append( openGLWidget )

	def updateOpenGLWidget( self ):
		'''	redraw all widget in openGL widget list
		'''

		#	loop over all openGL widget list and call redraw
		for openGLWidget in self.openGLWidgetList:
			openGLWidget.redraw()

class DisplayWindow( Fl_Gl_Window ):
	'''	this class designed for display window
	'''

	GrabSize = 10.0

	def __init__( self, x, y, w, h, pointHandler, l = 'DisplayWindow' ):
		'''	initialize class.
		'''
		Fl_Gl_Window.__init__( self, x, y, w, h, l )

		#	store point handler to member class
		self.pointHandler = pointHandler
		self.pointHandler.addOpenGLWidget( self )

		#	declare variable to store grab point object
		self.grabPointObject = None

	def draw( self ):
		'''	this function will override from fltk
		'''

		#	specify the lower left corner of the viewport rectangle, in pixels. 
		#		and size of the viewport
		GL.glViewport( 0, 0, self.w(), self.h() )

		#	set background color and opaque
		GL.glClearColor( 0.0, 0.0, 0.0, 0.0 )

		#	clear gl
		GL.glClearDepth( 0.0 )
		GL.glClear( GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT )

		#	setup smooth point
		GL.glEnable( GL.GL_BLEND )
		GL.glBlendFunc( GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA )
		GL.glEnable( GL.GL_POINT_SMOOTH )

		#	set matrix mode to projection
		GL.glMatrixMode( GL.GL_PROJECTION )

		#	reset the projection matrix
		GL.glLoadIdentity()

		#	orthographic projection (xLeft, xRight, yBottom, yTop, zNear, zFar)
		#		relative to camera's eye position.
		GL.glOrtho( -200, 200, -200, 200, -1, 1 )

		#	set matrix mode to model view
		GL.glMatrixMode( GL.GL_MODELVIEW )

		#	reset the projection matrix
		GL.glLoadIdentity()

		#	call render function 
		self.render()

	def handle( self, event ):
		'''	this function will override from fltk
		'''

		#	get fl event key
		key = Fl.event_key()

		#	get fl modifier
		modifier = Fl_event_alt() | Fl_event_ctrl() | Fl_event_shift()

		#	get mouse button
		mouseButton = Fl_event_button()

		#	get mouse position on image window
		x = Fl.event_x()
		y = Fl.event_y()

		#	create key dict
		keyDict = { 'modifier':modifier, 'key':key, 'mouseState':event }

		if  event in [ FL_PUSH, FL_DRAG, FL_RELEASE ]:

			#	get the modelview info
			modelview = GL.glGetDoublev( GL.GL_MODELVIEW_MATRIX )

			#	get the projection matrix info
			projection = GL.glGetDoublev( GL.GL_PROJECTION_MATRIX )

			#	get the viewport info
			viewport = GL.glGetIntegerv( GL.GL_VIEWPORT )

			#	get the world coordinates from the screen coordinates
			worldPosition = GLU.gluUnProject( x, viewport[3] - y, 0, modelview, projection, viewport )

			#	call the grab point event function
			self.grabPointEvent_callback( worldPosition[0], worldPosition[1], keyDict )
			return True

		return Fl_Gl_Window.handle( self, event )

	#
	#	Operation Function
	#

	def render( self ):
		'''	this function will render to OpenGL
		'''

		GL.glColor4f( 1.0, 1.0, 1.0, 1.0 )
		GL.glLineWidth( 1.0 )

		GL.glBegin( GL.GL_LINE_LOOP )
		GL.glVertex2f( self.pointHandler.llx, self.pointHandler.lly )
		GL.glVertex2f( self.pointHandler.urx, self.pointHandler.lly )
		GL.glVertex2f( self.pointHandler.urx, self.pointHandler.ury )
		GL.glVertex2f( self.pointHandler.llx, self.pointHandler.ury )
		GL.glEnd()

		#	loop over all point object in point list
		for pointObject in self.pointHandler.pointList:

			#	render point object
			pointObject.render()

	#
	#	Callback Function
	#

	def grabPointEvent_callback( self, sceneX, sceneY, keyDict ):
		'''	this function will grab point in openGL widget 
		'''

		if keyDict[ 'mouseState' ] == FL_PUSH:

			#	loop over all point object in point list
			for pointObject in self.pointHandler.pointList:

				#	check if point object out of grab radius
				#	so, continue
				if( not self.isGrabPointObject_internal( pointObject, sceneX, sceneY ) ):
					continue

				#	set grab point object
				self.grabPointObject = pointObject

				break

		elif keyDict[ 'mouseState' ] == FL_DRAG and self.grabPointObject != None:

			#	set point position
			self.setPointPosition_internal( sceneX, sceneY )
			
			#	call the redraw
			self.pointHandler.updateOpenGLWidget()

		elif keyDict[ 'mouseState' ] == FL_RELEASE:

			#	set grab point object to none
			self.grabPointObject = None

		self.redraw()

	#
	#	Internal Function
	#

	def isGrabPointObject_internal( self, pointObject, sceneX, sceneY ):
		'''	this function will return is grab point object or not
		'''

		#	get point position
		pointX, pointY = self.getPointPosition_internal( pointObject )

		#	check if point object out of grab radius
		#	so, continue
		if( ( ( pointX - sceneX )**2 + ( pointY - sceneY )**2 )**0.5 < DisplayWindow.GrabSize ):
			return True

		return False

	def getPointPosition_internal( self, pointObject ):
		'''	this function will return position from point object
		'''

		return pointObject.point.x, pointObject.point.y

	def setPointPosition_internal( self, pointX, pointY ):
		'''	this function will set position to point object
		'''

		self.grabPointObject.point.x = pointX
		self.grabPointObject.point.y = pointY

class SrcDisplayWindow( DisplayWindow ):

	def __init__( self, x, y, w, h, pointHandler ):
		'''	initialize class.
		'''
		DisplayWindow.__init__( self, x, y, w, h, pointHandler, 'Source Display Window' )

	def render( self ):
		'''	this function will render to OpenGL
		'''
		DisplayWindow.render( self )
		
		GL.glColor4f( 1.0, 0.0, 0.0, 1.0 )
		GL.glPointSize( 8.0 )
		GL.glLineWidth( 1.0 )
		
		GL.glBegin( GL.GL_POINTS )

		#	loop over all point object in point list
		for pointObject in self.pointHandler.pointList:
			GL.glVertex2f( pointObject.srcPoint.x, pointObject.srcPoint.y )
		
		GL.glEnd()

		GL.glBegin( GL.GL_LINE_LOOP )

		#	loop over all point object in point list
		for pointObject in self.pointHandler.pointList:
			GL.glVertex2f( pointObject.srcPoint.x, pointObject.srcPoint.y )
		
		GL.glEnd()

		GL.glPointSize( 3.0 )
		
		GL.glColor4f( 0.0, 1.0, 1.0, 1.0 )
		GL.glBegin( GL.GL_POINTS )

		warpCornerHandler_point = WarpCornerHandler( self.pointHandler.pointList[0].point, self.pointHandler.pointList[1].point,
								  					 self.pointHandler.pointList[2].point, self.pointHandler.pointList[3].point )

		for sv in range( 0, NumSamplingV + 1 ):
			for su in range( 0, NumSamplingU + 1 ):
				u = su * ( 1 / float( NumSamplingU ) )
				v = sv * ( 1 / float( NumSamplingV ) )

				x, y = warpCornerHandler_point.calculateXYFromUV( u, v )

				GL.glVertex2f( x, y )

		GL.glEnd()

	#
	#	Internal Function
	#

	def getPointPosition_internal( self, pointObject ):
		'''	this function will return position from point object
		'''

		return pointObject.srcPoint.x, pointObject.srcPoint.y

	def setPointPosition_internal( self, pointX, pointY ):
		'''	this function will set position to point object
		'''

		self.grabPointObject.srcPoint.x = pointX
		self.grabPointObject.srcPoint.y = pointY

class DstDisplayWindow( DisplayWindow ):

	def __init__( self, x, y, w, h, pointHandler ):
		'''	initialize class.
		'''
		DisplayWindow.__init__( self, x, y, w, h, pointHandler, 'Destination Display Window' )

	def render( self ):
		'''	this function will render to OpenGL
		'''
		DisplayWindow.render( self )

		GL.glColor4f( 0.0, 1.0, 0.0, 1.0 )
		GL.glPointSize( 8.0 )
		GL.glLineWidth( 1.0 )
		
		GL.glBegin( GL.GL_POINTS )

		#	loop over all point object in point list
		for pointObject in self.pointHandler.pointList:
			GL.glVertex2f( pointObject.dstPoint.x, pointObject.dstPoint.y )
		
		GL.glEnd()

		GL.glBegin( GL.GL_LINE_LOOP )

		#	loop over all point object in point list
		for pointObject in self.pointHandler.pointList:
			GL.glVertex2f( pointObject.dstPoint.x, pointObject.dstPoint.y )
		
		GL.glEnd()

		GL.glPointSize( 3.0 )
		
		GL.glColor4f( 0.0, 1.0, 1.0, 1.0 )
		GL.glBegin( GL.GL_POINTS )

		warpCornerHandler_point = WarpCornerHandler( self.pointHandler.pointList[0].point, self.pointHandler.pointList[1].point,
								  					 self.pointHandler.pointList[2].point, self.pointHandler.pointList[3].point )

		warpCornerHandler_src = WarpCornerHandler( self.pointHandler.pointList[0].srcPoint, self.pointHandler.pointList[1].srcPoint,
								  				   self.pointHandler.pointList[2].srcPoint, self.pointHandler.pointList[3].srcPoint )

		warpCornerHandler_dst = WarpCornerHandler( self.pointHandler.pointList[0].dstPoint, self.pointHandler.pointList[1].dstPoint,
								  				   self.pointHandler.pointList[2].dstPoint, self.pointHandler.pointList[3].dstPoint )

		for sv in range( 0, NumSamplingV + 1 ):
			for su in range( 0, NumSamplingU + 1 ):
				u = su * ( 1 / float( NumSamplingU ) )
				v = sv * ( 1 / float( NumSamplingV ) )

				try:

					x, y       = warpCornerHandler_point.calculateXYFromUV( u, v )
					srcU, srcV = warpCornerHandler_src.calculateUVFromXY( x, y )
					dstX, dstY = warpCornerHandler_dst.calculateXYFromUV( srcU, srcV )

					GL.glVertex2f( dstX, dstY )

				except Exception as e:
					print 'Can not warp this point.'
					pass

		GL.glEnd()

	#
	#	Internal Function
	#

	def getPointPosition_internal( self, pointObject ):
		'''	this function will return position from point object
		'''

		return pointObject.dstPoint.x, pointObject.dstPoint.y

	def setPointPosition_internal( self, pointX, pointY ):
		'''	this function will set position to point object
		'''

		self.grabPointObject.dstPoint.x = pointX
		self.grabPointObject.dstPoint.y = pointY

######################################################
#	Main Function

def main():
	'''	 get option and arguments before next process
	'''

	#	Initialize option parser
	parser = optparse.OptionParser( usage='%prog <arg1> <arg2> [options]',
									prog=ProgramName,
									version='Version :: {}'.format( ProgramVersion ) )

	#	-d  :: Enabled debug mode ( False )
	parser.add_option( '-d', dest='flagDebugMode', help='Enabled debug mode ( False )', 
						action='store_true', default=False )

	#	-l  :: Enabled log mode ( False )
	parser.add_option( '-l', dest='flagLogMode', help='Enabled log mode ( False )',
						action='store_true', default=False )

	#	Option and Arguments
	options, args = parser.parse_args()

	#	Check number of arguments
	if NumberRequireArgument != -1 and NumberRequireArgument != len( args ):

		print 'Check arguments, Because number of arguments is wrong!!!'
		print '>>> Terminate script'
		sys.exit( -1 )

	##################################################################################
	#
	#	Arguments
	#	

	# arg0 = args[0]
	# arg1 = args[1]

	##################################################################################
	#
	#	Option
	#

	flagDebugMode = options.flagDebugMode
	flagLogMode = options.flagLogMode

	##################################################################################
	#
	#	Represent
	#

	if flagDebugMode:
		print '>>> Debug mode has enabled.'

	if flagLogMode:
		print '>>> Log mode has enabled.'

	##################################################################################
	#
	#	My code
	#

	pointHandler = PointHandler( -150, -150, 150, 150 )

	pointHandler.addPoint( PointObject( -100, -100 ) )
	pointHandler.addPoint( PointObject(  100, -100 ) )
	pointHandler.addPoint( PointObject(  100,  100 ) )
	pointHandler.addPoint( PointObject( -100,  100 ) )

	# pointHandler.pointList[3].srcPoint.x = 0
	# pointHandler.pointList[3].srcPoint.y = 0

	srcDisplay = SrcDisplayWindow( 100, 150, 720, 480, pointHandler )
	dstDisplay = DstDisplayWindow( 920, 150, 720, 480, pointHandler )
	srcDisplay.show()
	dstDisplay.show()

	Fl.run()

if __name__ == '__main__':
	'''	this function for run code
	'''

	print '\nDescription :: {}\n'.format( ModuleDescription )

	#	Call main function
	main()
