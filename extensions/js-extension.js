function update_slider(frame_count) {
    //这里的代码将更新slider的最大值
    console.log("hello bro!");
    console.log("elements has been binding:", frameCount, frameSlider);
    frameCount.addEventListener("input", (e) => {
        console.log("frame count has been changed:", e);
    });
    let frameCountInput = frameCount.getElementsByTagName("input")[0]
    frameCountInput.addEventListener("input", (e) => {
        console.log("[input] frame count has been changed:", e);
    });
    frameCountInput.addEventListener("propertychange", (e) => {
        console.log("[propertychange] frame count(input) has been changed:", e);
    });
    frameCountInput.addEventListener("change", (e) => {
        console.log("[change] frame count has been changed:", e);
    });
}