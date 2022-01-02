console.clear();

var loginBtn = document.getElementById('login');
var signupBtn = document.getElementById('signup');

/* When the login button is clicked than the login window opens and the sing up window closes.
   If the login window was already open it closes and the sign up window opens instead. */
loginBtn.addEventListener('click', (e) => {
	let parent = e.target.parentNode.parentNode;
	Array.from(e.target.parentNode.parentNode.classList).find((element) => {
		if(element !== "slide-up") {
			parent.classList.add('slide-up')
		}else{
			signupBtn.parentNode.classList.add('slide-up')
			parent.classList.remove('slide-up')
		}
	});
});

/* When the sign up button is clicked than the sign up window opens and the login window closes
   If the sign up window was already open it closes and the login window opens instead. */
signupBtn.addEventListener('click', (e) => {
	let parent = e.target.parentNode;
	Array.from(e.target.parentNode.classList).find((element) => {
		if(element !== "slide-up") {
			parent.classList.add('slide-up')
		}else{
			loginBtn.parentNode.parentNode.classList.add('slide-up')
			parent.classList.remove('slide-up')
		}
	});
});