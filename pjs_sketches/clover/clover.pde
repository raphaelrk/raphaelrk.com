int dotsAmount = 36 * 6; // how many dots
int dotDiam = 10; // diameter of dots
int maxRadius = min(width, height) / 2; // how far out the dots go
double speed = 0.5; // multiplier to how fast the dots move
int opacity = 150; // opacity of dots
double gap = 360.0/dotsAmount*2.0; // frames it takes for one dot to go
                            // to the next one's position

void setup()
{
	// Set window size
	size(window.innerWidth, window.innerHeight);
	frameRate(60);
	colorMode(HSB);
}

void draw()
{
	// background
    background(255, 0, 250);
    
    int minScreenSize = min(width, height);
    dotDiam = minScreenSize / 40;
    maxRadius = minScreenSize / 2;

    pushMatrix();
        // move to center
        translate(width/2, height/2);
        
        // go through every dot
        for(int i = 0; i < dotsAmount; i++) {
            // rotate to face dot
            rotate(radians(360.0/dotsAmount));
            
            pushMatrix();
                // move to dot
                double t = frameCount*speed + i*gap;
                translate(0, maxRadius * sin(radians(t)));
                
                // set its color
                noStroke();
                fill(255.0/dotsAmount*i, 255, 255, opacity);
                
                // draw the dot
                ellipse(0, 0, dotDiam, dotDiam);
            popMatrix();
        }
    popMatrix();
}