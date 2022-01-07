 window.onload = () => {
    document.onwheel = customScrollFunction;
    function customScrollFunction(event){

    let deltaY = event.deltaY;
    let deltaYSign = Math.sign(deltaY);

    if(deltaYSign==-1){
        document.getElementById("scrl").scrollBy({
            top: 0,
            left: -169,
            behavior: 'auto'
          });
    }
    else{
        document.getElementById("scrl").scrollBy({
            top: 0,
            left: 169,
            behavior: 'auto'
        });
    }
   }
}