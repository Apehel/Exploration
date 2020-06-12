// Bibliothèque de scripts pour manipuler les objets du robot-explorer.
//
// Auteur : André-Pierre LIMOUZIN
// Version : 1.0 - 05.2020

var SCALE = 1;
var GRID = 100;


// Définition de la classe XMAP.
//
// Un objet XMAP est créé par un robot qui explore sont environnement.
// Il est constitué d'un tableau de plusieurs objets XNODE.
//
// Paramètre elMap : Elément XML dont le tagName est <map>.
// Propriété nodes : Tableau d'objets XNODE.
// Méthode draw : Représentation graphique de l'objet XMAP
function XMAP(elMap) {
    this.minX = getFloatAttribute(elMap, "minX");
    this.maxX = getFloatAttribute(elMap, "maxX");
    this.minY = getFloatAttribute(elMap, "minY");
    this.maxY = getFloatAttribute(elMap, "maxY");
    this.nodes = getArrayContent(elMap, "node", XNODE, this);
    this.draw = function(context) {
        for (iNode = 0; iNode < this.nodes.length; iNode++) {
            this.nodes[iNode].draw(context);
        }
    }
    this.robot2canvas = function(xPoint) {
        return new POINT(
            Math.round((xPoint.x - this.minX) * SCALE), 
            Math.round((this.maxY - xPoint.y) * SCALE));
    }
}

// Définition de la classe XNODE.
//
// Chaque objet XNODE correspond à une station du robot à partir de laquelle
// il effectue un tour d'horizon.
// Les points relevés par le tour d'horizon sont rangés dans une tableau d'objet XPOINT.
// Les coordonnées sont exprimées en Float dans le référentiel du robot.
// 
// Paramètre elNode : Elément XML dont le tagName est <node>.
// Paramètre map : Objet MAP auquel appartient l'objet XNODE.
// Propriété x : Abscisse de la station XNODE.
// Propriété y : Ordonnée de la station XNODE.
// Propriété points : Tableau d'objets XPOINT relevés par le tour d'horizon.
// Méthode draw : Représentation graphique de l'objet XNODE.
function XNODE(elNode, map) {
    this.map = map;
    this.x = getFloatAttribute(elNode, "x");
    this.y = getFloatAttribute(elNode, "y");
    this.orientation = getFloatAttribute(elNode, "orientation") * Math.PI /180.0;
    this.points = getArrayContent(elNode, "point", XPOINT, this);
    this.walls = getArrayContent(elNode, "wall", XWALL, this);
    this.draw = function(context) {
        var pt = this.map.robot2canvas(this);
        for(iPoint = 0; iPoint < this.points.length; iPoint++) {
            ipt = this.map.robot2canvas(this.points[iPoint]);
            drawLine(context, pt.x, pt.y, ipt.x, ipt.y, "#CFCFFF");
            this.points[iPoint].draw(context);
        }
        drawCircle(context, pt.x, pt.y, 20, "#FFFFFF", "#FFFFFF");
        drawCircle(context, pt.x, pt.y, 10, "#FF0000", "#FFFFFF");
        drawCircle(context, pt.x, pt.y, 6, "#FF0000", null);
        drawArrow(context, pt.x, pt.y, 5, this.orientation, "#FF000");
        for(iWall = 0; iWall < this.walls.length; iWall++) {
            this.walls[iWall].draw(context);
        }
    }
}

// Définition de la classe XWALL
//
// Un objet XWALL correspond à un mur relevé lors d'un tour d'horizon par le robot.
// Il est constittué d'une succession de points valides.
function XWALL(elWall, node) {
    this.node = node;
    this.map = node.map;
    var elPt1 = elWall.getElementsByTagName("Pt1")[0];
    var elPt2= elWall.getElementsByTagName("Pt2")[0];
    this.pt1 = new XPOINT(elPt1, this);
    this.pt2 = new XPOINT(elPt2, this);
    this.draw = function(context) {
        p1 = this.map.robot2canvas(this.pt1);
        p2 = this.map.robot2canvas(this.pt2);
        context.save();
        context.lineWidth = 4;
        drawLine(context, p1.x, p1.y, p2.x, p2.y, "#00007F");
        context.restore();
    }
}


// Définition de la classe XPOINT.
//
// Un objet XPOINT correspond à un point relevé lors d'un tour d'horizon par le robot.
// Les coordonnées sont exprimées en Float dans le référentiel du robot.
//
// Paramètre elPoint : Elément XML dont le tagName est <point>.
// Propriété x : Abscisse de l'objet XPOINT.
// Propriété y : Ordonnée de l'objet XPOINT.
// Méthode draw : Représentation graphique de l'objet XPOINT.
function XPOINT(elPoint, node) {
    this.node = node;
    this.map = node.map;
    this.x = getFloatAttribute(elPoint, "x");
    this.y = getFloatAttribute(elPoint, "y");
    this.isValid = getBooleanAttribute(elPoint, "valid")
    this.draw = function(context) {
        var pt = this.map.robot2canvas(this);
        context.fillStyle = "#5050FF";
        context.strokeStyle = "#5050FF";
        context.beginPath();
        context.arc(pt.x, pt.y, 5, 0, 2 * Math.PI);
        if (this.isValid) {
            context.fill();
        } else {
            context.stroke();
        }
    }
}

// Récupération d'un attribut XML de type Float.
// 
// el : Elément XML dans lequel se trouve l'attribut.
// name : Nom de l'attribut. 
// return : Valeur convertie en Float de l'attribut. 
function getFloatAttribute(el, name) {
    var attrValue = el.getAttribute(name);
    return attrValue == null ? 0.0 : parseFloat(attrValue);
}

// Récupération d'un attribut XML de type Integer.
//
// el : Elément XML dans lequel se trouve l'attribut.
// name : Nom de l'attribut. 
// return : Valeur convertie en Int de l'attribut. 
function getIntAttribute(el, name) {
    var attrValue = el.getAttribute(name);
    return attrValue == null ? 0 : parseInt(attrValue);
}

// Récupération d'un attribut XML de type Boolean.
//
// el : Elément XML dans lequel se trouve l'attribut.
// name : Nom de l'attribut. 
// return : Valeur convertie en Bool de l'attribut. 
function getBooleanAttribute(el, name) {
    var attrValue = el.getAttribute(name);
    return attrValue == "true" || attrValue == "True" || attrValue == "TRUE" || attrValue == "1";
}

// Récupération d'un tableau d'objets contenus dans un élément XML.
//
// el : Elément XML dans lequel se trouvent les objets.
// name : nom (tagName) des éléments contenus dans el.
// ctor : Constructeur à invoquer pour instancier l'objet à partir de son élément XML.
// parent: Objet parent qui encapsule les éléments du tableau.
function getArrayContent(el, name, ctor, parent) {
    var content = new Array();
    var childs = el.getElementsByTagName(name);
    for (var j = 0; j < childs.length; j++) {
        content[j] = new ctor(childs[j], parent);
    }
    return content;
}

// Conversion d'un point du référentiel du robot dans le référentiel du Canvas.
// Paramètre xPoint : objet XPOINT dont les coordonnées sont expérimée en Float dans le référentiel du robot.
// Propriété x : abscisse dans le référentiel du Canvas.
// Propriété y : ordonnée dans le référentiel du Canvas.  
function ROBOT2CANVAS(xPoint) {
    this.x = (ORIGIN.x + xPoint.x) * SCALE;
    this.y = (ORIGIN.y - xPoint.y) * SCALE;
}

// Définition de la classe POINT.
//
//La classe POINT définit un point dans le référentiel du Canvas.
// Les coordonnées sont exprimées en Integer.
// Propriété x : abscisse dans le référentiel du Canvas.
// Propriété y : ordonnée dans le référentiel du Canvas.  
function POINT(x0, y0) {
    this.x = x0;
    this.y = y0;
}

function drawCircle(context, x0, y0, R, fgColor, bgColor) {
    if (bgColor != null) {
	context.fillStyle = bgColor;
	context.beginPath();
	context.arc(x0, y0, R, 0, 2 * Math.PI);
	context.fill();
    }
    context.strokeStyle = fgColor;
    context.beginPath();
    context.arc(x0, y0, R, 0, 2 * Math.PI);
    context.stroke();
}

function drawLine(context, x1, y1, x2, y2, fgColor) {
    context.strokeStyle = fgColor;
    context.beginPath();
    context.moveTo(x1, y1);
    context.lineTo(x2, y2);
    context.stroke();
}

ARROW = [[0,-3],[0,4],[-1,2],[1,2]];

function drawArrow(context, x0, y0, R, orientation, fgColor) {
    context.save();
    context.strokeStyle = fgColor;
    context.lineWidth = 2;
    rotArrow = new Array(ARROW.length);
    sin = Math.sin(orientation);
    cos = Math.cos(orientation);
    for (k = 0; k < ARROW.length; k++) {
	pt = new Array(2);
	pt[0] = ARROW[k][0] * R * cos + ARROW[k][1] * R * sin;
	pt[1] = -ARROW[k][0] * R * sin + ARROW[k][1] * R * cos;
	rotArrow[k] = pt;
    }
    context.strokeStyle = fgColor;
    context.beginPath();
    context.moveTo(x0 + rotArrow[0][0], y0 - rotArrow[0][1]);
    context.lineTo(x0 + rotArrow[1][0], y0 - rotArrow[1][1]);
    context.moveTo(x0 + rotArrow[2][0], y0 - rotArrow[2][1]);
    context.lineTo(x0 + rotArrow[1][0], y0 - rotArrow[1][1]);
    context.moveTo(x0 + rotArrow[3][0], y0 - rotArrow[3][1]);
    context.lineTo(x0 + rotArrow[1][0], y0 - rotArrow[1][1]);
    context.stroke();
    context.restore();
}
