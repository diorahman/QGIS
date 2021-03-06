# -*- coding: utf-8 -*-
"""QGIS Unit tests for QgsComposerMap.

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""
__author__ = '(C) 2012 by Dr. Horst Düster / Dr. Marco Hugentobler'
__date__ = '20/08/2012'
__copyright__ = 'Copyright 2012, The QGIS Project'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

import os
import qgis
from PyQt4.QtCore import QFileInfo
from PyQt4.QtXml import QDomDocument
from PyQt4.QtGui import (QPainter,
                          QColor)

from qgis.core import (QgsComposerMap,
                       QgsRectangle,
                       QgsRasterLayer,
                       QgsComposition,
                       QgsMapRenderer,
                       QgsMapLayerRegistry,
                       QgsMultiBandColorRenderer
                     )
from utilities import (unitTestDataPath,
                       getQgisTestApp,
                       TestCase,
                       unittest,
                       expectedFailure
                      )
from qgscompositionchecker import QgsCompositionChecker

QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()
TEST_DATA_DIR = unitTestDataPath()


class TestQgsComposerMap(TestCase):

    def __init__(self, methodName):
        """Run once on class initialisation."""
        unittest.TestCase.__init__(self, methodName)
        myPath = os.path.join(TEST_DATA_DIR, 'landsat.tif')
        rasterFileInfo = QFileInfo(myPath)
        mRasterLayer = QgsRasterLayer(rasterFileInfo.filePath(),
                                      rasterFileInfo.completeBaseName())
        rasterRenderer = QgsMultiBandColorRenderer(
            mRasterLayer.dataProvider(), 2, 3, 4)
        mRasterLayer.setRenderer(rasterRenderer)
        #pipe = mRasterLayer.pipe()
        #assert pipe.set(rasterRenderer), 'Cannot set pipe renderer'
        QgsMapLayerRegistry.instance().addMapLayers([mRasterLayer])

        # create composition with composer map
        self.mMapRenderer = QgsMapRenderer()
        layerStringList = []
        layerStringList.append(mRasterLayer.id())
        self.mMapRenderer.setLayerSet(layerStringList)
        self.mMapRenderer.setProjectionsEnabled(False)
        self.mComposition = QgsComposition(self.mMapRenderer)
        self.mComposition.setPaperSize(297, 210)
        self.mComposerMap = QgsComposerMap(self.mComposition, 20, 20, 200, 100)
        self.mComposerMap.setFrameEnabled(True)
        self.mComposition.addComposerMap(self.mComposerMap)

    def testGrid(self):
        """Test that we can create a grid for a map."""
        myRectangle = QgsRectangle(781662.375, 3339523.125,
                                   793062.375, 3345223.125)
        self.mComposerMap.setNewExtent(myRectangle)
        self.mComposerMap.setGridEnabled(True)
        self.mComposerMap.setGridIntervalX(2000)
        self.mComposerMap.setGridIntervalY(2000)
        self.mComposerMap.setShowGridAnnotation(True)
        self.mComposerMap.setGridPenWidth(0.5)
        self.mComposerMap.setGridPenColor(QColor(0,255,0))
        self.mComposerMap.setGridAnnotationPrecision(0)
        self.mComposerMap.setGridAnnotationPosition(QgsComposerMap.Disabled,
                                                    QgsComposerMap.Left)
        self.mComposerMap.setGridAnnotationPosition(
            QgsComposerMap.OutsideMapFrame,
            QgsComposerMap.Right)
        self.mComposerMap.setGridAnnotationPosition(QgsComposerMap.Disabled,
                                                    QgsComposerMap.Top)
        self.mComposerMap.setGridAnnotationPosition(
            QgsComposerMap.OutsideMapFrame,
            QgsComposerMap.Bottom)
        self.mComposerMap.setGridAnnotationDirection(QgsComposerMap.Horizontal,
                                                     QgsComposerMap.Right)
        self.mComposerMap.setGridAnnotationDirection(QgsComposerMap.Horizontal,
                                                     QgsComposerMap.Bottom)
        self.mComposerMap.setAnnotationFontColor(QColor(255,0,0,150))
        self.mComposerMap.setGridBlendMode(QPainter.CompositionMode_Overlay)
        checker = QgsCompositionChecker('composermap_grid', self.mComposition)
        myTestResult, myMessage = checker.testComposition()
        self.mComposerMap.setGridEnabled(False)
        self.mComposerMap.setShowGridAnnotation(False)

        assert myTestResult == True, myMessage

    def testOverviewMap(self):
        overviewMap = QgsComposerMap(self.mComposition, 20, 130, 70, 70)
        overviewMap.setFrameEnabled(True)
        self.mComposition.addComposerMap(overviewMap)
        # zoom in
        myRectangle = QgsRectangle(785462.375, 3341423.125,
                                   789262.375, 3343323.125)
        self.mComposerMap.setNewExtent(myRectangle)
        myRectangle2 = QgsRectangle(781662.375, 3339523.125,
                                    793062.375, 3350923.125)
        overviewMap.setNewExtent(myRectangle2)
        overviewMap.setOverviewFrameMap(self.mComposerMap.id())
        checker = QgsCompositionChecker('composermap_overview', self.mComposition)
        myTestResult, myMessage = checker.testComposition()
        self.mComposition.removeComposerItem(overviewMap)
        assert myTestResult == True, myMessage

    def testOverviewMapBlend(self):
        overviewMap = QgsComposerMap(self.mComposition, 20, 130, 70, 70)
        overviewMap.setFrameEnabled(True)
        self.mComposition.addComposerMap(overviewMap)
        # zoom in
        myRectangle = QgsRectangle(785462.375, 3341423.125,
                                   789262.375, 3343323.125)
        self.mComposerMap.setNewExtent(myRectangle)
        myRectangle2 = QgsRectangle(781662.375, 3339523.125,
                                    793062.375, 3350923.125)
        overviewMap.setNewExtent(myRectangle2)
        overviewMap.setOverviewFrameMap(self.mComposerMap.id())
        overviewMap.setOverviewBlendMode(QPainter.CompositionMode_Multiply)
        checker = QgsCompositionChecker('composermap_overview_blending', self.mComposition)
        myTestResult, myMessage = checker.testComposition()
        self.mComposition.removeComposerItem(overviewMap)
        assert myTestResult == True, myMessage

    def testOverviewMapInvert(self):
        overviewMap = QgsComposerMap(self.mComposition, 20, 130, 70, 70)
        overviewMap.setFrameEnabled(True)
        self.mComposition.addComposerMap(overviewMap)
        # zoom in
        myRectangle = QgsRectangle(785462.375, 3341423.125,
                                   789262.375, 3343323.125)
        self.mComposerMap.setNewExtent(myRectangle)
        myRectangle2 = QgsRectangle(781662.375, 3339523.125,
                                    793062.375, 3350923.125)
        overviewMap.setNewExtent(myRectangle2)
        overviewMap.setOverviewFrameMap(self.mComposerMap.id())
        overviewMap.setOverviewInverted(True)
        checker = QgsCompositionChecker('composermap_overview_invert', self.mComposition)
        myTestResult, myMessage = checker.testComposition()
        self.mComposition.removeComposerItem(overviewMap)
        assert myTestResult == True, myMessage

    def testOverviewMapCenter(self):
        overviewMap = QgsComposerMap(self.mComposition, 20, 130, 70, 70)
        overviewMap.setFrameEnabled(True)
        self.mComposition.addComposerMap(overviewMap)
        # zoom in
        myRectangle = QgsRectangle(785462.375+5000, 3341423.125,
                                   789262.375+5000, 3343323.125)
        self.mComposerMap.setNewExtent(myRectangle)
        myRectangle2 = QgsRectangle(781662.375, 3339523.125,
                                    793062.375, 3350923.125)
        overviewMap.setNewExtent(myRectangle2)
        overviewMap.setOverviewFrameMap(self.mComposerMap.id())
        overviewMap.setOverviewInverted(False)
        overviewMap.setOverviewCentered(True)
        checker = QgsCompositionChecker('composermap_overview_center', self.mComposition)
        myTestResult, myMessage = checker.testComposition()
        self.mComposition.removeComposerItem(overviewMap)
        assert myTestResult == True, myMessage

    # Fails because addItemsFromXML has been commented out in sip
    @expectedFailure
    def testuniqueId(self):
        doc = QDomDocument()
        documentElement = doc.createElement('ComposerItemClipboard')
        self.mComposition.writeXML(documentElement, doc)
        self.mComposition.addItemsFromXML(documentElement, doc, 0, False)

        #test if both composer maps have different ids
        newMap = QgsComposerMap()
        mapList = self.mComposition.composerMapItems()

        for mapIt in mapList:
            if mapIt != self.mComposerMap:
              newMap = mapIt
              break

        oldId = self.mComposerMap.id()
        newId = newMap.id()

        self.mComposition.removeComposerItem(newMap)
        myMessage = 'old: %s new: %s'  % (oldId, newId)
        assert oldId != newId, myMessage

    def testZebraStyle(self):
        self.mComposerMap.setGridFrameStyle(QgsComposerMap.Zebra)
        myRectangle = QgsRectangle(785462.375, 3341423.125,
                                   789262.375, 3343323.125)
        self.mComposerMap.setNewExtent( myRectangle )
        self.mComposerMap.setGridEnabled(True)
        self.mComposerMap.setGridIntervalX(2000)
        self.mComposerMap.setGridIntervalY(2000)
        self.mComposerMap.setGridFrameWidth( 10 )
        self.mComposerMap.setGridFramePenSize( 1 )
        self.mComposerMap.setGridPenWidth( 0.5 )
        self.mComposerMap.setGridFramePenColor( QColor( 255, 100, 0, 200 ) )
        self.mComposerMap.setGridFrameFillColor1( QColor( 50, 90, 50, 100 ) )
        self.mComposerMap.setGridFrameFillColor2( QColor( 200, 220, 100, 60 ) )

        checker = QgsCompositionChecker('composermap_zebrastyle', self.mComposition)
        myTestResult, myMessage = checker.testComposition()
        assert myTestResult == True, myMessage

    def testWorldFileGeneration( self ):
        myRectangle = QgsRectangle(781662.375, 3339523.125, 793062.375, 3345223.125)
        self.mComposerMap.setNewExtent( myRectangle )
        self.mComposerMap.setMapRotation( 30.0 )

        self.mComposition.setGenerateWorldFile( True )
        self.mComposition.setWorldFileMap( self.mComposerMap )

        p = self.mComposition.computeWorldFileParameters()
        pexpected = (4.180480199790922, 2.4133064516129026, 779443.7612381146,
                     2.4136013686911886, -4.179969388427311, 3342408.5663611)
        ptolerance = (0.001, 0.001, 1, 0.001, 0.001, 1e+03)
        for i in range(0,6):
            assert abs(p[i]-pexpected[i]) < ptolerance[i]

if __name__ == '__main__':
    unittest.main()

