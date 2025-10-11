<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
    <xsl:param name="pTestParam"/>
    <xsl:param name="pTestParam2"/>
    <xsl:template match="/">
        <result>
            <param name="pTestParam"><xsl:value-of select="$pTestParam"/></param>
            <param name="pTestParam2"><xsl:value-of select="$pTestParam2"/></param>
            <xsl:apply-templates/>
        </result>
    </xsl:template>
    <xsl:template match="test">
        <element><xsl:value-of select="."/></element>
    </xsl:template>
</xsl:stylesheet>