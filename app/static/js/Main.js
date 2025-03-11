function HideNavBar(me){
    const  NavBar=document.getElementsByTagName('nav')[0];
    const Main=document.getElementsByTagName('main')[0];
    const Icon=document.getElementById('id_expand_arrow');
    
    is_closed = false;
    if(NavBar.style.display==='none'){
        is_closed=true;
    }

    if(is_closed){
        NavBar.style.display="block";
        Main.style.marginLeft='6rem';
        me.style.position='absolute';
        me.classList.remove('ExpandNavBarIconTop');
        Icon.classList.replace('fa-arrow-left','fa-arrow-right');
    }
    else{
        NavBar.style.display="none";
        Main.style.marginLeft='0.1rem';
        me.style.position='unset';
        me.classList.add('ExpandNavBarIconTop');
        Icon.classList.replace('fa-arrow-right','fa-arrow-left');
    }


}







function AJAX_Get_Revenue_for_two_reports(report_one_date,report_two_date){
    const data = {
        report_one_date: report_one_date,
        report_two_date: report_two_date
    };


    fetch('/CompareTwoReports', {
        method: 'POST', 
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data) // Send data as JSON
    })
    .then(response => response.json()) // Parse JSON from the server
    .then(result => {
        console.log('Response from server:', result);

        // Display the received data in the browser
        console.log("Server Net_Revenue_Aggregated says : ",result.Net_Revenue_Aggregated);
        console.log("Server Report_Date says : ",result.Report_Date);
        console.log("Server Report_Date_Two says : ",result.Report_Date_Two);
        
        //Changing values based on received new data
        report_one_and_two_dates=document.getElementById('report_one_and_two_dates');
        report_one_and_two_dates.innerHTML=result.Report_Date+"📋 <br> Compared to <br>"+result.Report_Date_Two+"📋";


        //constructing box per branch then at the end we add Total Box
        Net_Revenue_Aggregated=result.Net_Revenue_Aggregated
        HomePageTrends=document.getElementsByClassName('HomePageTrends')[0];
        console.log("HomePageTrends",HomePageTrends)
        HomePageTrends.innerHTML="";

        Net_Revenue_Aggregated.forEach(function(branch, index) {
            console.log(branch);

            Net_Revenue_Icon="fa-solid fa-arrow-trend-up"
            Net_Revenue_Trend="IncreaseArrow"
            if (branch[2]<0){
                Net_Revenue_Trend="DecreaseArrow"
                Net_Revenue_Icon="fa-solid fa-arrow-trend-down"


            }
            Labour_Trend="IncreaseArrow"
            Labour_Icon="fa-solid fa-arrow-trend-up"

            if(branch[4]<0){
                Labour_Trend="DecreaseArrow"
                Labour_Icon="fa-solid fa-arrow-trend-down"


            }
            HomePageTrends.innerHTML+=
            `
                <div class="RevenueTrend">
                    <div class="BranchRevenue">${branch[0]}</div>
                    <div class="MoneyEarned"><b>&#163; ${branch[1]}</b></div>
                    <div class="${Net_Revenue_Trend}"><i class="${Net_Revenue_Icon}"></i> ${branch[2]}%</div>
                    <div class="MoneyEarned"><b>${branch[3]}%</b></div>
                    <div class="${Labour_Trend}"><i class="${Labour_Icon}"></i> ${branch[4]}%</div>
                </div>
            `;
          });

    })
    .catch(error => {
        console.error('Error:', error);
    });
}


function AJAX_Update_Plot_Graph(specific_Item,branch,start_date,end_date,category_value){
    image_source=document.getElementById('id_graph_image_one').src ;

    plot_details={
        specific_Item:specific_Item,
        start_date:start_date,
        end_date:end_date,
        branch:branch,
        type_of_graph:id_graph_type.value,
        type_of_trend:id_trend_type.value,
        category:category_value,
    }

    fetch('/Update_Plot_Graph', {
        method: 'POST', 
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(plot_details) 
    })
    .then(response => response.json())
    .then(result => {
        document.getElementById('id_graph_image_one').src= 'data:image/png;base64,' + result.image;

    })
}



//Updates both items and categories
function AJAX_Update_Branch_Specific_Items_Graph(branch){
    data={branch:branch}

    fetch('/Update_Branch_Specific_Items_Graph', {
        method: 'POST', 
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data) // Send data as JSON
    })
    .then(response => response.json()) // Parse JSON from the server
    .then(result => {
        all_specific_items=result.all_specific_items
        all_categories=result.all_categories

        document.getElementById('id_specific_item_graph_one').innerHTML="";
        document.getElementById('id_category_breakdown').innerHTML="";

        for (let index = 0; index < all_specific_items.length; index++) {
            console.log(all_specific_items[index]);
            let option = document.createElement('option');
            option.value = all_specific_items[index];
            option.text = all_specific_items[index];
            document.getElementById('id_specific_item_graph_one').append(option);

        }

        for (let index = 0; index < all_categories.length; index++) {
            console.log(all_categories[index]);
            let option = document.createElement('option');
            option.value = all_categories[index];
            option.text = all_categories[index];
            document.getElementById('id_category_breakdown').append(option);

        }
    });

}

function UpdateRedMessageBox(){
    console.log(localStorage.getItem('RedMessageValue'))

    // var RedMessageValue=document.getElementById("id_red_message_box_value");


    RedMessageValue=localStorage.getItem('RedMessageValue');



    var RedMessageBox=document.querySelector('.RedMessageBox');
    var RedIcon=document.querySelector('.fa-users')
    if (RedMessageValue==0){
        RedMessageBox.style.display="none";
        RedIcon.classList.remove('fa-beat');
        RedMessageBox.innerHTML=RedMessageValue;
        RedMessageBox.style.display="none";


    }
    else if(RedMessageValue>99){
        RedMessageBox.innerHTML="+99";
        RedMessageBox.innerHTML=RedMessageValue;
        RedMessageBox.style.display="block";

    }
    else{
        RedMessageBox.style.display="block";
        RedIcon.classList.add('fa-beat');
        RedMessageBox.innerHTML=RedMessageValue;
        RedMessageBox.style.display="block";

    }
}

document.addEventListener('DOMContentLoaded', function() {
    window.onload = function() {
        // var RedMessageBox=document.querySelector('.RedMessageBox');
        // if(RedMessageBox){
        //     AJAX_Notifications_New_Accounts();
        //     UpdateRedMessageBox();
        // }

    }


    // console.log("Current Page is",window.location.pathname);
    const CurrentPage = window.location.pathname;
    const RestOfPages=document.querySelectorAll('.Navigation_Link')
    // const AllIcons=document.querySelectorAll(".NavIconSelectedCurrently")
    // console.log("Rest Of Pages is",RestOfPages);

    RestOfPages.forEach(Page => {
        // console.log("Inside ForEach",Page);
        if (Page.pathname===CurrentPage){
            // console.log("True",Page,CurrentPage);
            // console.log(Page.getElementsByTagName('div'))
            Page.classList.add('NavSelectedCurrently')
            Page.getElementsByTagName('div')[0].classList.add('NavIconSelectedCurrently')
            
        }
        else{
            // console.log("False",Page,CurrentPage)
            Page.classList.remove('NavSelectedCurrently')
            Page.getElementsByTagName('div')[0].classList.remove('NavIconSelectedCurrently')
        }
    });

    //Checking if Account Management red bubble contains 0 or not ,if it is 0 then hide the red bubble else show it


    var RedMessageBox=document.querySelector('.RedMessageBox');
    var RedIcon=document.querySelector('.fa-users')
    var RedMessageValue=document.getElementById("id_red_message_box_value");

    if(RedMessageBox){
        console.log("RedMessageBox",RedMessageBox);
        console.log("RedMessageValue",RedMessageValue);
    }

    function Get_Two_Reports_Revenue(report_two_changed,report_one_changed,report_one_date,report_two_date){
        if(report_one_changed && report_two_changed){

            if (report_one_changed && report_two_changed){
                AJAX_Get_Revenue_for_two_reports(report_one_date,report_two_date)            
            }

        }
    }
    id_report_comparsion_one=document.getElementById("id_report_comparsion_one");
    id_report_comparsion_two=document.getElementById("id_report_comparsion_two");

    let report_one_changed=false;
    let report_two_changed=false;
    let report_one_date;
    let report_two_date;

    if(id_report_comparsion_one){
    id_report_comparsion_two.addEventListener("change",function(){
        report_two_changed=true;
        report_one_date=this.value;
        Get_Two_Reports_Revenue(report_one_changed,report_two_changed,report_one_date,report_two_date);

    })

    id_report_comparsion_one.addEventListener("change",function(){
        report_one_changed=true;
        report_two_date=this.value;
        Get_Two_Reports_Revenue(report_one_changed,report_two_changed,report_one_date,report_two_date);

    });
    

    }


    //Running UpdateRedMessageBox as soon as the page is loaded for the first time

    // RedMessageValue.addEventListener("input",UpdateRedMessageBox)

    const id_update_graph_one=document.getElementById("id_update_graph_one");
    const id_specific_item_graph_one=document.getElementById("id_specific_item_graph_one");
    const id_branch_one=document.getElementById("id_branch_one");
    const id_start_one=document.getElementById("id_start_one");
    const id_end_one=document.getElementById("id_end_one");

    if(id_branch_one){
        id_branch_one.addEventListener("change",()=>{

            AJAX_Update_Branch_Specific_Items_Graph(id_branch_one.value);



        })
    }
    if(id_update_graph_one){

        id_update_graph_one.addEventListener("click",() =>{
            specific_Item=id_specific_item_graph_one.value
            branch=id_branch_one.value
            start_date=id_start_one.value
            end_date=id_end_one.value
            category=id_category.value
            AJAX_Update_Plot_Graph(specific_Item,branch,start_date,end_date,category);
        });
    }


    const id_graph_type = document.getElementById('id_graph_type');
    const id_trend_type = document.getElementById('id_trend_type');
    const id_category= document.getElementById('id_category_breakdown');
    const id_specific_item=document.getElementById('id_specific_item_graph_one');

    if(id_graph_type){
        id_graph_type.addEventListener('change',()=>{
            if(id_graph_type.value=="Specific Item Graph Net Sale"){
            }
            if (id_graph_type.value=="Specific Item Graph" || id_graph_type.value=="Specific Item Graph Net Sale"){
                id_trend_type.style.display="none";
                id_start_one.style.display="block";
                id_end_one.style.display="block";
                id_category.style.display="none";
                id_specific_item.style.display="block";
            }


            else if(id_graph_type.value=="Category BreakDown Graph"){
                id_category.style.display="block";
                id_trend_type.style.display="none";
                // id_start_one.style.display="none";
                // id_end_one.style.display="none";
                id_specific_item.style.display="none";

            }
            else{
                id_trend_type.style.display="block";
                // id_start_one.style.display="none";
                // id_end_one.style.display="none";
                id_category.style.display="none";
                id_specific_item.style.display="block";

            }

        })
    }



});