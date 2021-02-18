
console.log("You are in controlroom.js");

function DemoFunctionSuccess(data){
    console.log("Inside Demo Fucntion Success");
    console.log(data);
    document.getElementById("CurrentDateTime").innerText = data;

}

function DemoFunction(){
    SubmitFormAJAX('demo_form', success_func = DemoFunctionSuccess);
}