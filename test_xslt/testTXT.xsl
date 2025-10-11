<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="text" encoding="UTF-8"/>
    <xsl:param name="pTestParam"/>
    <xsl:param name="pTestParam2"/>
    <xsl:param name="extraParam"/>
    <xsl:template match="/">
        <xsl:value-of select="$pTestParam"/>,<xsl:value-of select="$pTestParam2"/>,<xsl:value-of select="$extraParam"/>
        <xsl:apply-templates/>
    </xsl:template>
    <xsl:template match="test">
        <xsl:text>,</xsl:text><xsl:value-of select="."/>
    </xsl:template>
</xsl:stylesheet>