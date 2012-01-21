<?xml version="1.0"?>
<xsl:stylesheet
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

    <!-- **********************************************************************
         Projects - CSV Import Stylesheet

         2011-12-15 / Dominic König <dominic[AT]aidiq[DOT]com>

         CSV column...........Format..........Content

         Name.................string..........Project Name
         Description..........string..........Project short description
         Objectives...........string..........Project objectives
         StartDate............YYYY-MM-DD......Start date of the project
         EndDate..............YYYY-MM-DD......End date of the project
         Countries............comma-sep list..List of country names or ISO codes
         Departments..........comma-sep list..List of Organisation Sectors (Departments)
         HostOrganisation.....string..........Name of the Host Organisation
         Hazards..............comma-sep list..List of Hazard names
         Themes...............comma-sep list..List of Theme names
         HFA..................comma-sep list..List of HFA priorities (integer numbers)
         FPFirstName..........string..........First Name of Focal Person
         FPLastName...........string..........Last Name of Focal Person
         FPEmail..............string..........Email Address of Focal Person
         FPMobilePhone........string..........Mobile Phone Number of Focal Person

    *********************************************************************** -->

    <xsl:output method="xml"/>

    <xsl:include href="../../xml/commons.xsl"/>
    <xsl:include href="../../xml/countries.xsl"/>

    <xsl:variable name="SectorPrefix" select="'Sector:'"/>
    <xsl:variable name="HazardPrefix" select="'Hazard:'"/>
    <xsl:variable name="ThemePrefix" select="'Theme:'"/>

    <xsl:key name="orgs"
             match="row"
             use="col[@field='HostOrganisation']"/>

    <!-- ****************************************************************** -->
    <xsl:template match="/">
        <s3xml>
            <xsl:apply-templates select="./table/row"/>
            <xsl:for-each select="//row[generate-id(.)=
                                        generate-id(key('orgs',
                                                        col[@field='HostOrganisation'])[1])]">
                <xsl:call-template name="Organisation"/>
            </xsl:for-each>
        </s3xml>
    </xsl:template>

    <!-- ****************************************************************** -->
    <xsl:template match="row">

        <xsl:variable name="Name" select="col[@field='Name']"/>
        <xsl:variable name="Description" select="col[@field='Description']"/>
        <xsl:variable name="StartDate" select="col[@field='StartDate']"/>
        <xsl:variable name="EndDate" select="col[@field='EndDate']"/>
        <xsl:variable name="Objectives" select="col[@field='Objectives']"/>
        <xsl:variable name="OrgName" select="col[@field='HostOrganisation']/text()"/>

        <xsl:variable name="Countries" select="col[@field='Countries']"/>

        <xsl:variable name="Sectors" select="col[@field='Departments']"/>
        <xsl:variable name="Hazards" select="col[@field='Hazards']"/>
        <xsl:variable name="Themes" select="col[@field='Themes']"/>

        <xsl:variable name="HFA" select="col[@field='HFA']"/>

        <xsl:variable name="FirstName" select="col[@field='FPFirstName']/text()"/>
        <xsl:variable name="LastName" select="col[@field='FPLastName']/text()"/>

        <resource name="project_project">
            <xsl:attribute name="tuid">
                <xsl:value-of select="concat('Project:', $Name)"/>
            </xsl:attribute>
            <data field="name"><xsl:value-of select="$Name"/></data>
            <data field="description"><xsl:value-of select="$Description"/></data>
            <data field="start_date"><xsl:value-of select="$StartDate"/></data>
            <data field="end_date"><xsl:value-of select="$EndDate"/></data>
            <data field="objectives"><xsl:value-of select="$Objectives"/></data>

            <xsl:if test="$HFA!=''">
                <data field="hfa">
                    <xsl:attribute name="value">
                        <xsl:value-of select="concat('[', $HFA, ']')"/>
                    </xsl:attribute>
                </data>
            </xsl:if>

            <reference field="countries_id" resource="gis_location">
                <xsl:attribute name="uuid">
                    <xsl:variable name="CountryCodes">
                        <xsl:call-template name="splitList">
                            <xsl:with-param name="arg">countrycode</xsl:with-param>
                            <xsl:with-param name="list">
                                <xsl:value-of select="$Countries"/>
                            </xsl:with-param>
                        </xsl:call-template>
                    </xsl:variable>
                    <xsl:if test="starts-with($CountryCodes, ',&quot;')">
                        <xsl:value-of select="concat('[', substring-after($CountryCodes, ','), ']')"/>
                    </xsl:if>
                </xsl:attribute>
            </reference>

            <reference field="sector_id" resource="org_sector">
                <xsl:attribute name="tuid">
                    <xsl:variable name="SectorList">
                        <xsl:call-template name="quoteList">
                            <xsl:with-param name="prefix"><xsl:value-of select="$SectorPrefix"/></xsl:with-param>
                            <xsl:with-param name="list"><xsl:value-of select="$Sectors"/></xsl:with-param>
                        </xsl:call-template>
                    </xsl:variable>
                    <xsl:value-of select="concat('[', $SectorList, ']')"/>
                </xsl:attribute>
            </reference>

            <reference field="multi_hazard_id" resource="project_hazard">
                <xsl:attribute name="tuid">
                    <xsl:variable name="HazardList">
                        <xsl:call-template name="quoteList">
                            <xsl:with-param name="prefix"><xsl:value-of select="$HazardPrefix"/></xsl:with-param>
                            <xsl:with-param name="list"><xsl:value-of select="$Hazards"/></xsl:with-param>
                        </xsl:call-template>
                    </xsl:variable>
                    <xsl:value-of select="concat('[', $HazardList, ']')"/>
                </xsl:attribute>
            </reference>

            <reference field="multi_theme_id" resource="project_theme">
                <xsl:attribute name="tuid">
                    <xsl:variable name="ThemeList">
                        <xsl:call-template name="quoteList">
                            <xsl:with-param name="prefix"><xsl:value-of select="$ThemePrefix"/></xsl:with-param>
                            <xsl:with-param name="list"><xsl:value-of select="$Themes"/></xsl:with-param>
                        </xsl:call-template>
                    </xsl:variable>
                    <xsl:value-of select="concat('[', $ThemeList, ']')"/>
                </xsl:attribute>
            </reference>

            <reference field="human_resource_id" resource="hrm_human_resource">
                <xsl:attribute name="tuid">
                    <xsl:value-of select="concat('HR:', $LastName, ',', $FirstName)"/>
                </xsl:attribute>
            </reference>

            <resource name="project_organisation">
                <data field="role">1</data>
                <reference field="organisation_id" resource="org_organisation">
                    <xsl:attribute name="tuid">
                        <xsl:value-of select="concat('ProjectOrganisation:', $OrgName)"/>
                    </xsl:attribute>
                </reference>
            </resource>

        </resource>

        <xsl:call-template name="splitList">
            <xsl:with-param name="list"><xsl:value-of select="$Sectors"/></xsl:with-param>
            <xsl:with-param name="arg">sector</xsl:with-param>
        </xsl:call-template>

        <xsl:call-template name="splitList">
            <xsl:with-param name="list"><xsl:value-of select="$Hazards"/></xsl:with-param>
            <xsl:with-param name="arg">hazard</xsl:with-param>
        </xsl:call-template>

        <xsl:call-template name="splitList">
            <xsl:with-param name="list"><xsl:value-of select="$Themes"/></xsl:with-param>
            <xsl:with-param name="arg">theme</xsl:with-param>
        </xsl:call-template>

        <xsl:call-template name="FocalPerson"/>

    </xsl:template>

    <!-- ****************************************************************** -->
    <xsl:template name="resource">
        <xsl:param name="item"/>
        <xsl:param name="arg"/>

        <xsl:choose>
            <!-- Country reference list -->
            <xsl:when test="$arg='countrycode'">
                <xsl:variable name="CountryCode">
                    <xsl:choose>
                        <xsl:when test="string-length($item)!=2">
                            <xsl:call-template name="countryname2iso">
                                <xsl:with-param name="country">
                                    <xsl:value-of select="$item"/>
                                </xsl:with-param>
                            </xsl:call-template>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:value-of select="$item"/>
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:variable>
                <xsl:value-of select="concat(',&quot;', 'urn:iso:std:iso:3166:-1:code:', $CountryCode, '&quot;')"/>
            </xsl:when>
            <!-- Sector list -->
            <xsl:when test="$arg='sector'">
                <resource name="org_sector">
                    <xsl:attribute name="tuid">
                        <xsl:value-of select="concat($SectorPrefix, $item)"/>
                    </xsl:attribute>
                    <data field="name"><xsl:value-of select="$item"/></data>
                    <data field="abrv"><xsl:value-of select="$item"/></data>
                </resource>
            </xsl:when>
            <!-- Hazard list -->
            <xsl:when test="$arg='hazard'">
                <resource name="project_hazard">
                    <xsl:attribute name="tuid">
                        <xsl:value-of select="concat($HazardPrefix, $item)"/>
                    </xsl:attribute>
                    <data field="name"><xsl:value-of select="$item"/></data>
                </resource>
            </xsl:when>
            <!-- Theme list -->
            <xsl:when test="$arg='theme'">
                <resource name="project_theme">
                    <xsl:attribute name="tuid">
                        <xsl:value-of select="concat($ThemePrefix, $item)"/>
                    </xsl:attribute>
                    <data field="name"><xsl:value-of select="$item"/></data>
                </resource>
            </xsl:when>
        </xsl:choose>
    </xsl:template>

    <!-- ****************************************************************** -->
    <xsl:template name="Organisation">
        <xsl:variable name="OrgName" select="col[@field='HostOrganisation']/text()"/>

        <resource name="org_organisation">
            <xsl:attribute name="tuid">
                <xsl:value-of select="concat('ProjectOrganisation:', $OrgName)"/>
            </xsl:attribute>
            <data field="name"><xsl:value-of select="$OrgName"/></data>
        </resource>

    </xsl:template>

    <!-- ****************************************************************** -->
    <xsl:template name="FocalPerson">
        <xsl:variable name="FirstName" select="col[@field='FPFirstName']/text()"/>
        <xsl:variable name="LastName" select="col[@field='FPLastName']/text()"/>
        <xsl:variable name="Email" select="col[@field='FPEmail']/text()"/>
        <xsl:variable name="MobilePhone" select="col[@field='FPMobilePhone']/text()"/>
        <xsl:variable name="OrgName" select="col[@field='HostOrganisation']/text()"/>

        <resource name="pr_person">
            <xsl:attribute name="tuid">
                <xsl:value-of select="concat('Person:', $LastName, ',', $FirstName)"/>
            </xsl:attribute>
            <data field="first_name"><xsl:value-of select="$FirstName"/></data>
            <data field="last_name"><xsl:value-of select="$LastName"/></data>
            <xsl:if test="$Email!=''">
                <resource name="pr_contact">
                    <data field="contact_method" value="EMAIL"/>
                    <data field="value"><xsl:value-of select="$Email"/></data>
                </resource>
            </xsl:if>
            <xsl:if test="$MobilePhone!=''">
                <resource name="pr_contact">
                    <data field="contact_method" value="SMS"/>
                    <data field="value"><xsl:value-of select="$MobilePhone"/></data>
                </resource>
            </xsl:if>
        </resource>

        <resource name="hrm_human_resource">
            <xsl:attribute name="tuid">
                <xsl:value-of select="concat('HR:', $LastName, ',', $FirstName)"/>
            </xsl:attribute>
            <data field="type">1</data> <!-- Staff -->
            <!-- Link to Organisation -->
            <reference field="organisation_id" resource="org_organisation">
                <xsl:attribute name="tuid">
                    <xsl:value-of select="concat('ProjectOrganisation:', $OrgName)"/>
                </xsl:attribute>
            </reference>
            <reference field="person_id" resource="pr_person">
                <xsl:attribute name="tuid">
                    <xsl:value-of select="concat('Person:', $LastName, ',', $FirstName)"/>
                </xsl:attribute>
            </reference>
        </resource>

    </xsl:template>

    <!-- ****************************************************************** -->

</xsl:stylesheet>
