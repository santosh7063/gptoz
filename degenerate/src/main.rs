extern crate image;
extern crate rand;

mod ghostmesh;

use ghostmesh::ghostmesh;


fn main() {

    let width = 4000;
    let height = 4000;

    // Create a new ImgBuf with width: width and height: height
    let mut imgbuf = image::ImageBuffer::new(width, height);

    // Iterate over the coordinates and pixels of the image
    for (_, _, pixel) in imgbuf.enumerate_pixels_mut() {
        *pixel = image::Luma([0]);
    }

    let zs = ghostmesh(width, height);

    for (x, y, pixel) in imgbuf.enumerate_pixels_mut() {
        *pixel = image::Luma([(zs[x as usize][y as usize] * 255.) as u8]);
    }

    imgbuf.save("image.png").unwrap();
}
