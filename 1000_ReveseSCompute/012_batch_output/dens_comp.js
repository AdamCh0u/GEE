//## paras
var year_dic = ee.Dictionary({34:1985,33:1986,32:1987,31:1988,
          30:1989,29:1990,28:1991,27:1992,26:1993,25:1994,24:1995,23:1996,22:1997,21:1998,
          20:1999,19:2000,18:2001,17:2002,16:2003,15:2004,14:2005,13:2006,12:2007,11:2008,
          10:2009, 9:2010, 8:2011, 7:2012, 6:2013, 5:2014, 4:2015, 3:2016, 2:2017, 1:2018,}) 
print(year_dic.get(34))// key has to be string
print(year_dic.get("34"));
		//[...Array(5).keys()]
var year = 1996
var year_key = ee.List.sequence(34,1,-1).map(function(i){
  return ee.String(i)
})
var year_value =ee.List.sequence(1985,2018,1)
var year_dic = ee.Dictionary.fromLists(year_key,year_value)


// ## GAIA
var image40 = ee.Image("users/zhouzz400/GAIA_2018_lat/GAIA_1985_2018_40"),
    image41 = ee.Image("users/zhouzz400/GAIA_2018_lat/GAIA_1985_2018_41"),
    image42 = ee.Image("users/zhouzz400/GAIA_2018_lat/GAIA_1985_2018_42");

var GAIA = ee.ImageCollection([image40,image41,image42])
  .mosaic();
var gaia_viz = {min:0,max:4,palette:["000000","FF0000"]}
Map.addLayer(GAIA, gaia_viz);


// ## water 
// var water1 = ee.Image("JRC/GSW1_1/MonthlyHistory/2006_01").gte(2)

// var water2 = ee.Image("JRC/GSW1_1/YearlyHistory/1996").gte(2)
// var water3 = ee.Image("JRC/GSW1_1/YearlyHistory/1996").gte(2)
var water = ee.Image("JRC/GSW1_1/YearlyHistory/1996").neq(1)
var water_viz = {min:0,max:3,palette:["ff0000","ffffff","99d9ea","0000ff"]};
// 红 白 青 蓝
// No data no water Seasonal water Permanent water


var waterornot_viz = {min:0,max:1,palette:["ff0000","ffffff"]}
Map.addLayer(water1,waterornot_viz);
//Map.addLayer(water2,viz);

//## center
var fid = ee.Number(85977539);
var center = ee.FeatureCollection("users/zhouzz400/Boundries/city_center")
  .filter(ee.Filter.eq("wof_id",fid)).geometry();
Map.addLayer(center);

//## 
var year_dic = ee.List([34,24]);
print(year_dic);
var GAIA_year = GAIA.gte(24);

var center = ee.FeatureCollection("users/zhouzz400/Boundries/city_center")
  .filter(ee.Filter.eq("wof_id",fid)).geometry();
Map.addLayer(center);


// ## compute new york a year
var GAIA_year = GAIA.gte(24);
// create buffer ring loop

var dis_list = ee.List.sequence(1000,30000,1000)

var buffer = dis_list.map(function (dis){
	return center.buffer(dis) );
})

// no need to create ring?
var  dis = 10000
buffer = buffer.add( center.buffer(dis) );
ring = ring.add( buffer.get(0));


var GAIA_year = GAIA.gte(24);
var dis_list = ee.List.sequence(1000,30000,1000)
var buffer_list = dis_list.map(function (dis){
	return center.buffer(dis) ;
})
print(buffer_list.length())
Map.addLayer(ee.Geometry(buffer_list.get(1)))
for (var i=0;i<buffer_list.length();i++){
  Map.addLayer(ee.Geometry(buffer_list.get(i)))
}
//####### solution 1 
function getArea(dis){
  var buffer = center.buffer(dis)
  var buffer_urban = GAIA_year.eq(1).clip(buffer)// in function 
  var area_imag = buffer_urban.multiply(ee.Image.pixelArea())
  var sumarea = ee.Number(area_imag.reduceRegion(
                  {"reducer": ee.Reducer.sum(),
                  "scale": 30,
                  "maxPixels": 1e9})
                  .get("b1") )
  return sumarea
}
var area = dis_list.map(getArea)
print(area)

//###### solution 2 with break in loop



Map.addLayer(ee.Geometry(ring.get(0)));
var ring_urban = GAIA_year.eq(1).clip(ring.get(0))
var urban_image = ring_urban.multiply(ee.Image.pixelArea())
var urban_area = ee.Number( 
  urban_image.reduceRegion({"reducer": ee.Reducer.sum(),"scale": 30,"maxPixels": 1e9}).get("b1") )

print(urban_area)


//#### 
//https://developers.google.com/earth-engine/tutorial_js_03
// use map instead
for (var i = 0; i < buffer_number ; i++) {
  var dis = 1000*(i+1)
  // ## ring 
  if (i===0){
    var ring = center.buffer(dis)
  }
  else{
    var ring = center.buffer(dis).symmetricDifference(center.buffer(dis-1000))
  }
  
  var areaL_total = areaL_total.add(ring.area());
  
  var area_urban = getArea(ring,GAIA_year,"b1");
  var areaL_urban = areaL_urban.add(area_urban);
  
  //var area_water = getArea(ring,water,"waterClass");
  //var areaL_urban = areaL_urban.add(area_water);
}


//###################################################################################

print(center.coordinates())
var ring = ee.Algorithms.GeometryConstructors.LinearRing(center.coordinates())
print(ring)




var area_l = ee.List([])
for (var i = 0; i < 30 ; i++) {
  var area = getArea(buffer_list.get(i),GAIA_year)
  area_l = area_l.add(area)
  
}
print(area_l)

// how to use iterate
var algorithm = function(current, previous) {
  previous = ee.List(previous);
  var n1 = ee.Number(previous.get(-1));
  var n2 = ee.Number(previous.get(-2));
  return previous.add(n1.add(n2));
};

// Compute 10 iterations.
var numIteration = ee.List.repeat(1, 10);
var start = [0, 1];
var sequence = numIteration.iterate(algorithm, start);
print(sequence);  // [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]

var previous = ee.List([0, 1])
var n1 = ee.Number(previous.get(-1));
var n2 = ee.Number(previous.get(-2));
print( previous.add(n1.add(n2)))


//############################################################################
// get dens
var coun_boun = ee.FeatureCollection("users/zhouzz400/Boundries/ne_10m_admin_0_countries")
  .filter(ee.Filter.eq("NAME",coun_name)).geometry()
  print(coun_boun)
Map.addLayer(coun_boun)
var coun_name = "France"
var coun_boun = table.filter(ee.Filter.eq("NAME",coun_name)).geometry()
print(coun_boun)
Map.addLayer(coun_boun)

var centers= ee.FeatureCollection("users/zhouzz400/Boundries/city_center")
  .filterBounds(coun_boun)
var dic = centers.toDictionary(["NAMEASCII","wof_id"])// ???
print(dic)
print(centers)
Map.addLayer(centers)
// ##############################################33
//## paras
var year = 1996
var year_key = ee.List.sequence(34,1,-1).map(function(i){
  return ee.String(i)
})
var year_value =ee.List.sequence(1985,2018,1)
var year_dic = ee.Dictionary.fromLists(year_key,year_value)


// ## GAIA
var image40 = ee.Image("users/zhouzz400/GAIA_2018_lat/GAIA_1985_2018_40"),
    image41 = ee.Image("users/zhouzz400/GAIA_2018_lat/GAIA_1985_2018_41"),
    image42 = ee.Image("users/zhouzz400/GAIA_2018_lat/GAIA_1985_2018_42");

var GAIA = ee.ImageCollection([image40,image41,image42])
  .mosaic();
//var gaia_viz = {min:0,max:4,palette:["000000","FF0000"]}
//Map.addLayer(GAIA, gaia_viz);

// ## center
var fid = ee.Number(85977539);
var center = ee.FeatureCollection("users/zhouzz400/Boundries/city_center")
  .filter(ee.Filter.eq("wof_id",fid)).geometry();
//Map.addLayer(center);

// ## water
var water = ee.Image("JRC/GSW1_1/YearlyHistory/1996").neq(1)
//var water_viz = {min:0,max:3,palette:["ff0000","ffffff","99d9ea","0000ff"]};


// ## buffer loop
var GAIA_year = GAIA.gte(24);
var dis_list = ee.List.sequence(1000,30000,1000)
var catArray = denDic(dis_list);
print(catArray);

Export.image.toDrive({
  image: landsat,
  description: 'imageToDriveExample',
  scale: 30,
  region: geometry
});

ar year_water = "1985" //water year has to be string
var water = getWater(year_water)
print(water)
function getWater(year_v){
  var water_y = ee.ImageCollection("JRC/GSW1_1/YearlyHistory")
    .filterMetadata("system:index","equals",year_v).first()
  return water_y
}

function centerToRe(center,year_x){
  var GAIA=  getGAIA(center);
  var water = ee.ImageCollection("JRC/GSW1_1/YearlyHistory/").neq(1)

  var GAIA_year = GAIA.gte(year_x);
  var dis_list = ee.List.sequence(1000,30000,1000);
  var catArray = denDic(dis_list);
  return carArray;
}

function getGAIA(center){
  var region = center.buffer(31000)
  var GAIA = imgc.filterBounds(region).mosaic()
  return GAIA
}
// ## 
function getUrban(dis){
  var buffer = center.buffer(dis);
  var buffer_urban = GAIA_year.eq(1).clip(buffer);// in function 
  var area_imag = buffer_urban.multiply(ee.Image.pixelArea());
  var sumarea = ee.Number(area_imag.reduceRegion(
                  {"reducer": ee.Reducer.sum(),
                  "scale": 30,
                  "maxPixels": 1e9})
                  .get("b1") );
  return sumarea;
}
// ## 
function getWater(dis){
  var buffer = center.buffer(dis);
  var buffer_urban = water.eq(1).clip(buffer);// in function 
  var area_imag = buffer_urban.multiply(ee.Image.pixelArea());
  var sumarea = ee.Number(area_imag.reduceRegion(
                  {"reducer": ee.Reducer.sum(),
                  "scale": 30,
                  "maxPixels": 1e9})
                  .get("waterClass") );// bandname changed;
  return sumarea;
}
// ##
function getTotal(dis){
  return center.buffer(dis).area();
}
// ## internal subtract 
function interSubt(list1){
  var list2 = list1.rotate(1);
  list2 = list2.set(0,0);
  var delta = ee.Array(list2).subtract(ee.Array(list1));
  return delta;
}


function denArray(dis_list){
  // ## comput dens circle
  var areaA_total = interSubt(dis_list.map(getTotal));
  var areaA_urban = interSubt(dis_list.map(getUrban));
  var areaA_water = interSubt(dis_list.map(getWater));
  
  var dens = areaA_urban.divide(areaA_total.subtract(areaA_water));
  var catArray = ee.Array.cat([areaA_total,areaA_urban,areaA_water,dens],1);
  return catArray;
}

//##############################################################################
// should be work
// but there seem to be some wrong with aside
var coun_name = "France"
var coun_boun = ee.FeatureCollection("users/zhouzz400/Boundries/ne_10m_admin_0_countries")
  .filter(ee.Filter.eq("NAME",coun_name)).geometry()

var centers= ee.FeatureCollection("users/zhouzz400/Boundries/city_center")
  .filterBounds(coun_boun)
var centersL = centers.toList(4000)

var result = centersL.map(centerToR)

print(result)

function centerToR(center){
  center = ee.Geometry(center)
  var GAIA=  getGAIA(center);
  var water = ee.Image("JRC/GSW1_1/YearlyHistory/2000").neq(1)
  
  var GAIA_year = GAIA.gte(19);
  var dis_list = ee.List.sequence(1000,30000,1000);
  var catArray = denArray(dis_list,center,GAIA_year,water);
  return catArray;
}
function getGAIA(center){
  var region = center.buffer(31000)
  var GAIA = ee.ImageCollection("users/zhouzz400/GAIA").filterBounds(region).mosaic()
  return GAIA
}
// ## 
function getUrban(dis,center,GAIA_year){
  var buffer = center.buffer(dis);
  var buffer_urban = GAIA_year.eq(1).clip(buffer);// in function 
  var area_imag = buffer_urban.multiply(ee.Image.pixelArea());
  var sumarea = ee.Number(area_imag.reduceRegion(
                  {"reducer": ee.Reducer.sum(),
                  "scale": 30,
                  "maxPixels": 1e9})
                  .get("b1") );
  return sumarea;
}
// ## 
function getWater(dis,center,water){
  var buffer = center.buffer(dis);
  var buffer_urban = water.eq(1).clip(buffer);// in function 
  var area_imag = buffer_urban.multiply(ee.Image.pixelArea());
  var sumarea = ee.Number(area_imag.reduceRegion(
                  {"reducer": ee.Reducer.sum(),
                  "scale": 30,
                  "maxPixels": 1e9})
                  .get("waterClass") );// bandname changed;
  return sumarea;
}
// ##
function getTotal(dis,center){
  return center.buffer(dis).area();
}
// ## internal subtract 
function interSubt(list1){
  var list2 = list1.rotate(1);
  list2 = list2.set(0,0);
  var delta = ee.Array(list2).subtract(ee.Array(list1));
  return delta;
}


function denArray(dis_list,center,GAIA_year,water){
  // ## comput dens circle
  var areaA_total = interSubt(dis_list.aside(getTotal,center));
  var areaA_urban = interSubt(dis_list.aside(getUrban,center,GAIA_year));
  var areaA_water = interSubt(dis_list.aside(getWater,center,water));
  
  var dens = areaA_urban.divide(areaA_total.subtract(areaA_water));
  var catArray = ee.Array.cat([areaA_total,areaA_urban,areaA_water,dens],1);
  return catArray;
}

//############################################################################


var coun_name = "France"
var coun_boun = ee.FeatureCollection("users/zhouzz400/Boundries/ne_10m_admin_0_countries")
  .filter(ee.Filter.eq("NAME",coun_name)).geometry()
var GAIA = ee.ImageCollection("users/zhouzz400/GAIA")
  .filterBounds(coun_boun).mosaic()

var water = ee.Image("JRC/GSW1_1/YearlyHistory/2000").neq(1)
var GAIA_year = GAIA.gte(19);
var dis = ee.List.sequence(1000,30000,1000);

var centers= ee.FeatureCollection("users/zhouzz400/Boundries/city_center")
  .filterBounds(coun_boun)
var centersL = centers.toList(4000)
for (var i=0;i<centersL.length();i++) {
  var center = centersL.get(i).geometry();
  var catArray = denDic(dis_list);
  print(catArray)

}

//################test
//var centersL = centers.toList(4000)
// ##############for and list [i]
// var centersL = ["a","b"]
// print(centersL[1])
// for (var i=0 ;i< centersL.length;i++){
//   print(centersL[i])
// }
// ##############for and list [i]
var centersL = ee.List(["a","b"])
print(centersL.get(1))
for (var i=0 ;i< centersL.length;i++){
  print(centersL.get(i))
}

var x = centers.map(function(center){
  center =ee.Feature(center).geometry();
  return center.area()
})
print(x)

//var demo = getUrban(1000,center,GAIA_year)
var lis = ee.apply(len,{a:3});
function len(a){
  return a;
}
var demo = ee.List([132,3]).aside(len,"In2012")
print(lis);

// ############################ get all 
var buffer_list = ee.List.sequence(1000,30000,1000)

var coun_name = "France"
var coun_boun = ee.FeatureCollection("users/zhouzz400/Boundries/ne_10m_admin_0_countries")
  .filter(ee.Filter.eq("NAME",coun_name)).geometry()

var centers= ee.FeatureCollection("users/zhouzz400/Boundries/city_center")
  .filterBounds(coun_boun)
var centersL = centers.toList(4000)
//print(centersL)
var cenindexlist = ee.List([1,3,4])
var x  = cenindexlist.map(function (index) {
  var center = centersL.get(index);
  var center1 = ee.Feature(center).geometry();
  return center1;
})
//print(x)
var a1 = ee.Array([1,2,4]).repeat(1,2)
var a2 = ee.Array([3,4,5]).repeat(0,2)
var a3 = ee.Array([2,4,5])
var a4 = ee.Array.cat([a1,a2],1)
//var a5 = ee.Array.cat([a4,a3],1)
print(a1)

// var mapL = ee.List([1,2,4])
// var mapR = ee.List([3,4,5])
// var map = centersL.zip(mapR)
// print(map)
// for (var i = 0; i<centersL.length();i++){
//   var dic = ee.Dictionary({})
//   center = centersL.get(i).geometry();
//   dic["center"] = center
//   print(dic)
//   var mapL = mapL.add(dic)
// }
// for (var i in centersL ){
//   var dic = ee.Dictionary({})
//   dic["center"] = ee.Feature(centersL.getGeometry(i)).geometry()
//   mapL = mapL.add(dic)
// }
// for (var i in centersL){
//   print(i)

//   var center = centersL.getGeometry(i);
//   mapL[i] = center
// }
var mapL = centersL.map(function(center){
  var center1 = ee.Feature(center).geometry();
  return center1
})

print(mapL)