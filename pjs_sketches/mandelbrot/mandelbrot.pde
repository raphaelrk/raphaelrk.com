/**
 * Mandelbrot
 * Program by Raphael-Rouvinov Kats
 * */

void setup() {
  size(window.innerWidth, window.innerHeight);
  //size(400, 400);
  //frame.setResizable(true);
  frameRate(10000);
  colorMode(HSB);
  strokeWeight(1);
}

int baseB = 20, //base brightness
    maxB = 500, // brightness of set
    maxIters = 500, // how many iterations done before stopping
    maxItersChange = 50, // how many more iterations allowed for every zoom-in
    maxD = 2; // max distance for mandelbrot before you know it's going out of bounds

int hueMult = 100;
int sat = 255;

float lBound = -maxD,
      rBound = maxD,
      tBound = -maxD,
      bBound = maxD;

int lastClickFrame = 0;

int aaLevel = 2;
double aaDist = 0.4;

double[] calcIters(double origX, double origY, double lastX, double lastY, double thisIteration) {
    //[new value] = [old-value]^2 + [original-value]
    double newX = origX + lastX*lastX - lastY * lastY;
    double newY = origY + 2*lastX*lastY;
    //newX -= 1/newX;
    //newY -= 1/newY;
    
    // from wiki article: perdiocity checking. Sometimes the same value just keeps popping up
    if(newX == lastX && newY == lastY) {
      double[] ret = {maxIters, lastX, lastY};
      return ret;
    }
    
    double d = Math.sqrt(newX * newX + newY * newY); // dist from (0, 0) to (newX, newY)
    
    if(d >= maxD) {
        double[] ret = {thisIteration, lastX, lastY};
        return ret;
    } else if(thisIteration >= maxIters) {
        double[] ret = {maxIters, lastX, lastY};
        return ret;
    } else {
        return calcIters(origX, origY, newX, newY, thisIteration+1);
    }
};

color getColAt(double x, double y) {
    double[] iters = calcIters(x, y, x, y, 1);
    
    double h = map((float)iters[0], 0, maxIters, 0, 255) * 2 % 255; 
    //double h = Math.sin(iters[0]/180*Math.PI) * 127+127;
    //double h = iters[0] + 1 - Math.log(Math.log(Math.sqrt(iters[1]*iters[1]+iters[2]*iters[2])))/Math.log(2);
    //double h = 2 - Math.log(Math.log(Math.sqrt(iters[1]*iters[1]+iters[2]*iters[2]))/Math.log(2))/Math.log(2);
    //       h *= 255;
    int s = 255;
    double b = 0;
    if(iters[0] != maxIters) {
      b = map((float)iters[0], 0, maxIters, 255, 50);
    }
    //double b = 255-map((float)iters[0], 0, maxIters, 0, 255);
    //double b = (iters[0] == maxIters) ? 0 : 255;
    
    return color((int)h, s, (int)b);
};

float getMedian(float[] arr) {
    arr = sort(arr); // sort array ascending
    if(arr.length % 2 == 0) {
        return (arr[floor(arr.length/2)] + arr[ceil(arr.length/2)])/2;
    } else {
        return arr[ceil(arr.length/2)];
    }
};

void draw() {
    int frame = frameCount-lastClickFrame,
        c = frame % width,
        minSize = min(width, height);
    
    noStroke();
    
    // println(map(mouseX, 0, minSize, tBound, bBound)); // testing locations
    
    // draw current horizontal
    loadPixels();
    for(int r = 0; r < height; r ++) { // loop through y pixels
      
        float testX = map(c, 0, minSize, lBound, rBound);
        float testY = map(r, 0, minSize, tBound, bBound);
        
        // has this already been drawn?
        if(testY > 0 && -testY > tBound) {
            // if so, use already calculated pixel
            int usedR = (int) map(-testY, tBound, bBound, 0, height);
            pixels[r*width + c] = pixels[usedR*width + c];
            continue;
        } 
        
        // from wikipedia: is this in the cardioid/period-2 bulb?
        double q = (testX-0.25)*(testX-0.25)+testY*testY;
        boolean inCardioid = q*(q+testX-0.25) < 0.25*testY*testY;
        boolean inP2bulb = (testX+1)*(testX+1) + testY*testY < 0.0625;
        if(inCardioid || inP2bulb) {
          pixels[r*width + c] = color(0, 0, 0);
          continue;
        }
        
        // variable to store hue/sat/bri of pixels used in antialiasing
        float[] hues = new float[aaLevel * aaLevel],
                sats = new float[aaLevel * aaLevel],
                bris = new float[aaLevel * aaLevel];
        
        for(int aliasRow = 0; aliasRow < aaLevel; aliasRow++) {
          for(int aliasCol = 0; aliasCol < aaLevel; aliasCol++) {
            // pixel "row" and "column" that will be sampled from
            double r2 = r + aaDist - aaDist*2/(aaLevel-1) * aliasRow, 
                   c2 = c + aaDist - aaDist*2/(aaLevel-1) * aliasCol;
            
            if(aaLevel % 2 == 0) {
              int r2Direction = (r2 >= aaLevel/2) ? 1 : -1;
              r2 = r + (aaDist - aaDist/(aaLevel-1) * aliasRow) * r2Direction;
              
              int c2Direction = (c2 >= aaLevel/2) ? 1 : -1;
              c2 = c + (aaDist - aaDist/(aaLevel-1) * aliasCol) * c2Direction;
              
            }
            
            double x = map((float)c2, 0, minSize, lBound, rBound);
            double y = map((float)r2, 0, minSize, tBound, bBound);
            
            color hsb = getColAt(x, y);
            hues[aliasRow+aliasCol] = hue(hsb);
            sats[aliasRow+aliasCol] = saturation(hsb);
            bris[aliasRow+aliasCol] = brightness(hsb);
          }
        }
        
        /**
        color hsb1 = getColAt(x, y);
        color hsb2 = getColAt(x, y2);
        color hsb3 = getColAt(x2, y);
        color hsb4 = getColAt(x2, y2);
        
        float[] hues = {hue(hsb1), hue(hsb2), hue(hsb3), hue(hsb4)};
        float[] sats = {saturation(hsb1), saturation(hsb2), 
                    saturation(hsb3), saturation(hsb4)};
        float[] bris = {brightness(hsb1), brightness(hsb2), 
                    brightness(hsb3), brightness(hsb4)};
        */
        // fill with median
        color colour = color(getMedian(hues), getMedian(sats), getMedian(bris));
        
        pixels[r*width + c] = colour;
    }
    updatePixels();
    
    if(frame < width) { // line
        stroke(0, 0, 255, 100);
        //line(c + 1, 0, c + 1, height);
    }
};

void mouseClicked() {
    //int minSize = min(width, height);
    lBound = map(mouseX-width/4, 0, width, lBound, rBound);
    rBound = map(mouseX+width/4, 0, height, lBound, rBound);
    tBound = map(mouseY-height/4, 0, height, tBound, bBound);
    bBound = tBound + (rBound - lBound);
    maxIters += maxItersChange;
    lastClickFrame = frameCount;
};

