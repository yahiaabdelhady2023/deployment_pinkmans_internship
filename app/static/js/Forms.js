document.addEventListener('DOMContentLoaded', function() {

    function ValidatePasswords(){
        if(id_password.value!=id_confirmpassword.value){
            id_confirmpassword.setCustomValidity("The Two passwords do not match");
        }
        else{
            id_confirmpassword.setCustomValidity("");
        }
    }
    function ForenameChecker(){
        console.log("value for forename is",id_forename.value);
        length_of_forename=id_forename.value.length;
        console.log("length of forename is",length_of_forename);
        if((/^[A-Za-z]+$/.test(id_forename.value[0]) && length_of_forename>0)){

        first_letter=id_forename.value[0].toUpperCase();   
        id_forename.value=first_letter+id_forename.value.slice(1, length_of_forename);
        }
    }

    function ChangePasswordLock(passwordlock_icon,passwordunlocked,password_field){
        temp1=window.getComputedStyle(passwordlock_icon)
        temp2=window.getComputedStyle(passwordunlocked)
        temp2=temp2.display
        temp1=temp1.display

        passwordlock_icon.style.display=temp2
        passwordunlocked.style.display=temp1
        console.log("temp1 display",temp1)
        console.log(id_passwordunlocked_icon.style.display)

        //changing password attributes [text/password]

        new_attribute=passwordlock_icon.style.display ==="block" ? "password":"text"
        password_field.type=new_attribute
    }

    console.log('The DOM has fully loaded');
    
    //constants for input field elements
    
    const id_password=document.getElementById("id_password");
    //constants for password lock icon elements
    const id_passwordlock_icon=document.getElementById("id_passwordlock_icon");
    const id_passwordunlocked_icon=document.getElementById("id_passwordunlocked_icon");
    const id_company_code=document.getElementById('id_company_code');

    //buttons for submission
    const id_register_button=document.getElementById("id_register_button");

    if(id_passwordlock_icon && id_passwordunlocked_icon){
        console.log("id_passwordlock_icon and id_passwordunlocked_icon works");
        id_passwordlock_icon.addEventListener('click', () => ChangePasswordLock(id_passwordlock_icon, id_passwordunlocked_icon,id_password));
        id_passwordunlocked_icon.addEventListener('click', () => ChangePasswordLock(id_passwordlock_icon, id_passwordunlocked_icon,id_password));

    }


    
    if(id_register_button){
        console.log("id_register_button works",id_register_button);
        id_register_button.addEventListener("submit", function(event)
        {   
           
        });
    }

    else{ console.log('id_register_button is not recognised here');}



   

});
