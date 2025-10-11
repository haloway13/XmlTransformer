<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="html" encoding="UTF-8"/>

    <xsl:param name="pTestParam"/>
    <xsl:param name="pTestParam2"/>
    <xsl:param name="extraParam"/>

    <xsl:template match="/">
        <xsl:message>pTestParam: <xsl:value-of select="$pTestParam"/></xsl:message>
        <xsl:message>pTestParam2: <xsl:value-of select="$pTestParam2"/></xsl:message>
        <xsl:message>extraParam: <xsl:value-of select="$extraParam"/></xsl:message>
        <html>
            <body>
                <p>Parameter pTestParam: <xsl:value-of select="$pTestParam"/></p>
                <p>Parameter pTestParam2: <xsl:value-of select="$pTestParam2"/></p>
                <p>Parameter extraParam: <xsl:value-of select="$extraParam"/></p>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>