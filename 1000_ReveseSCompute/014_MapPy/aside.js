//####################################
//####################################
var coun_name = "France"
var coun_boun = ee.FeatureCollection("users/zhouzz400/Boundries/ne_10m_admin_0_countries")
  .filter(ee.Filter.eq("NAME",coun_name)).geometry()

var water = ee.Image("JRC/GSW1_1/YearlyHistory/1996").neq(1)
var GAIA = ee.ImageCollection("users/zhouzz400/GAIA").filterBounds(coun_boun).mosaic()
var GAIA_year = GAIA.gte(19);

var centers= ee.FeatureCollection("users/zhouzz400/Boundries/city_center")
  .filterBounds(coun_boun)
var centersL = centers.toList(4000)

var mapL = centersL.slice(1,10).map(function(cen){
  var center = ee.Feature(cen).geometry();
  var dis_list = ee.List.sequence(1000,30000,1000);
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
  var areaA_total = interSubt(dis_list.map(getTotal));
  var areaA_urban = interSubt(dis_list.map(getUrban));
  var areaA_water = interSubt(dis_list.map(getWater));
  var dens = areaA_urban.divide(areaA_total.subtract(areaA_water));
  var catArray = ee.Array.cat([areaA_total,areaA_urban,areaA_water,dens],1);
  return catArray
})

print(mapL)

/// #####################################################
//####################################
var country  = "China"
var year = "1996"
var index = "0_10"
var coun_boun = ee.FeatureCollection("users/zhouzz400/Boundries/ne_10m_admin_0_countries")
  .filter(ee.Filter.eq("NAME",country)).geometry()

var water = ee.Image("JRC/GSW1_1/YearlyHistory/1996").neq(1)
var GAIA = ee.ImageCollection("users/zhouzz400/GAIA")
  .filterBounds(coun_boun).mosaic()
Map.addLayer(GAIA,{min:0,max:34,palatte:["FFFFFF","FF0000"]});
var GAIA_year = GAIA.gte(19);

var centers= ee.FeatureCollection("users/zhouzz400/Boundries/city_center")
  .filterBounds(coun_boun)
var centersL = centers.toList(4000).slice(0,10)
print(centersL)

var Ltotal = centersL.map(function(cen){
  var center = ee.Feature(cen).geometry();
  var dis_list = ee.List.sequence(1000,30000,1000);
  // ##
  function getTotal(dis){
    return center.buffer(dis).area();
  }
  var areaA_total = dis_list.map(getTotal);
  return areaA_total
})
print(Ltotal)


var Lurban = centersL.map(function(cen){
  var center = ee.Feature(cen).geometry();
  var dis_list = ee.List.sequence(1000,30000,1000);
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
  var areaA_urban = dis_list.map(getUrban);
  return areaA_urban
})
print(Lurban)

var Lwater = centersL.map(function(cen){
  var center = ee.Feature(cen).geometry();
  var dis_list = ee.List.sequence(1000,30000,1000);
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
  var areaA_water = dis_list.map(getWater);
  return areaA_water
})
print(Lwater)

var catArray = ee.Array.cat([Lwater],1);

var ex = ee.FeatureCollection([
  ee.Feature(coun_boun,{year :catArray})
  ])
Export.table.toDrive({
  collection: ex,
  description: year+country +index ,
  fileFormat: 'CSV'
});


ConnectionAbortedError: [WinError 10053] 你的主机中的软件中止了一个已建立的连接。
