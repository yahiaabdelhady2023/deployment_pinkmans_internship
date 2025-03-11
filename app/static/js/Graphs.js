var Current_Graph;
var dataset_element //Global variable these two

function update_table(columns,columns_dataset,columns_two,columns_dataset_two){
    id_expand_table=document.getElementById('id_expand_table')
    // id_expand_table.innerHTML='<i class="fa-solid fa-arrow-down"></i>'
    id_expand_table.style.display="none"
    // columns_dataset=columns_dataset
    console.log("columns",columns)
    console.log("columns_dataset",columns_dataset);
    table=document.getElementById('id_full_information_table');
    table_header=document.getElementsByTagName('thead')[0];
    tabletwo=document.getElementById('id_full_information_table_two');

    
    table.innerHTML=""
    tabletwo.innerHTML="";
    // table.innerHTML="" //clearing out the table children
    console.log(table);

    //Constructing table one first [for Lead_Type]
    if(columns_dataset_two){
    if(columns_dataset_two.length > 0) {
        console.log("data.columns_two",columns_two)
        console.log(columns_dataset_two)
        InsertData_to_Table(tabletwo,columns_two,columns_dataset_two)
    }
}
    InsertData_to_Table(table,columns,columns_dataset)
    function InsertData_to_Table(table_to_populate,Header_columns,value_columns_dataset){

    New_Row = table_to_populate.insertRow();

    for (let index = 0; index < Header_columns.length; index++) {
        New_Cell = New_Row.insertCell(index)  
        New_Cell.innerHTML='<th>'+Header_columns[index]+'</th>'    
        New_Cell.classList.add("Blue");
    }



    max_elements_to_show=10;

    rows_array=Object.values(value_columns_dataset)
    for (let index = 0; index < rows_array.length; index++) {
        console.log("rows_array",Object.values(rows_array[index]))
        
        row_values=Object.values(rows_array[index])

        New_Row = table_to_populate.insertRow();
        column_index=0
        row_values.forEach(value => {
            New_Cell = New_Row.insertCell(column_index)
            column_index++  
            New_Cell.innerHTML=value 
        });
        console.log(New_Row.cells[0])
        if (index>=max_elements_to_show && New_Row.cells[0].innerHTML!="Total"){
            New_Row.style.display="none"
            if (table.style.display=="table") {
                id_expand_table.style.display="block"

            }
        }


        
    }
}//END OF NESTED FUNCTION


}


function DisplayNewReport(branch_clicked){

    //All Trends
    id_trend_report_date=document.getElementById('id_trend_report_date')
    id_trend_report_branches=document.getElementById('id_trend_report_branches')
    id_trend_top_category=document.getElementById('id_trend_top_category')
    id_trend_top_item=document.getElementById('id_trend_top_item')
    id_trend_top_revenue=document.getElementById('id_trend_top_revenue')
    


    branchname=branch_clicked.getAttribute("data-branchname")
    id_report_to_select=document.getElementById('id_report_to_select').value;
    report_type_id_value=document.getElementById('id_report_type_id').value
    SelectorGraph=document.getElementById('SelectorGraph');
    id_date_from=document.getElementById('id_date_from').value;
    id_date_to=document.getElementById('id_date_to').value;

    // alert(id_report_to_select)
    console.log(report_type_id_value)
    console.log(document.getElementById('report_type_id_value'))
    report_type_text = SelectorGraph.options[SelectorGraph.selectedIndex].text;
    report_type_id_report_type = SelectorGraph.options[SelectorGraph.selectedIndex].value;
    console.log("Before sending , report_type_id_report_type is",report_type_id_report_type)
    // alert(report_type_id_report_type)
    showLoading()
    console.log("New Report details ==>",[branchname,id_date_from,report_type_text])
    // alert(report_type_text)
    fetch('/DisplayNewReport',{
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        // body: JSON.stringify([branchname,id_report_type_id,report_type_text,id_date_from,id_date_to])
         body: JSON.stringify([branchname,id_date_from,id_date_to,report_type_text,report_type_id_report_type])

    })
    .then(response => {

        return response.json();
    })
    .then(data => {
        console.log("Data Received for new Report is",data)
        hideLoading()
        if(data.columns_dataset_two){

            update_table(data.columns,data.columns_dataset,data.columns_two,data.columns_dataset_two);
        }else{

            update_table(data.columns,data.columns_dataset);
        }

        

        id_trend_report_date.innerHTML="Data is Based on Report "+data.Report_Date+"📋"
        id_trend_report_branches.innerHTML="Branch(s): "+data.branchname +"☕"
        id_trend_top_revenue.innerHTML="Total Revenue: "+data.Total_Net_Sales + " &#163; 💷"
        if(data.Top_Category){
            id_trend_top_category.innerHTML="Most Sold Category: "+data.Top_Category + "🍪"
            id_trend_top_category.style.display="block"
            id_trend_top_item.innerHTML="Most Sold Item: "+data.Top_Item + "🥐"
            id_trend_top_item.style.display="block"

        }
        else{
            id_trend_top_category.style.display="none"
            id_trend_top_item.style.display="none"
        }
        // console.log("Current_Graph",Current_Graph)
        // Current_Graph.destroy();
        // CreateGraph(id_graph_element,"pie",data.dataset);
        
        Current_Graph.data.labels=data.label_names
        Current_Graph.data.datasets[0].data=data.data_values
        Current_Graph.update();
        dataset_element=data.dataset;
        
    })
    .catch(error => {
        hideLoading();
        alert("Error: Report with such date does not exist.");
        console.error("Fetch failed:", error.message);
    });
    
}


function showLoading() {
    document.getElementById("loading-overlay").classList.remove("hidden");
}

function hideLoading() {
    document.getElementById("loading-overlay").classList.add("hidden");

}
document.addEventListener('DOMContentLoaded', function() {
    
    const id_report_to_select=document.getElementById('id_report_to_select');
    const SelectorGraph=document.getElementById('SelectorGraph');
    
    id_automation_manual_selector=document.getElementById('id_automation_manual_selector');
    if(id_automation_manual_selector){
        id_automation_manual_selector.addEventListener('change',function(e){
            value_Selected=id_automation_manual_selector.value

            var options = SelectorGraph.options;

            for (var option of options) {
                if (option.getAttribute('data-operation-type')==value_Selected) {
                    option.style.display="block";
                }
                else{
                    option.style.display="none";
                }
                // console.log(`Value: ${option.getAttribute('data-operation-type')}, Text: ${option.text}`);
            }
        });
    }

    id_expand_table=document.getElementById('id_expand_table');
    if (id_expand_table){

    is_arrow_down=true;
    const max_number_of_rows_to_display=10;
    id_expand_table.addEventListener("click", function(){
        table=document.getElementById('id_full_information_table');
        if (is_arrow_down) {
            is_arrow_down=false;
            id_expand_table.innerHTML='<i class="fa-solid fa-circle-up"></i>'
            for (let index = 0; index < table.rows.length; index++) {
                table.rows[index].style.display=""
                
            }
        }
        else{
            id_expand_table.innerHTML='<i class="fa-solid fa-circle-down"></i>'
            is_arrow_down=true;
            for (let index = 0; index < table.rows.length; index++) {
                if(index>=max_number_of_rows_to_display+1 && table.rows[index].cells[0].innerHTML!="Total"){
                    table.rows[index].style.display="none"
                }

                else{

                    table.rows[index].style.display=""
                }
                
            }
        }
    
    })
    }


    var xml = new XMLHttpRequest();

    if(id_report_to_select){
        // report_type_id_value GetReportDates
        // SelectorGraph.addEventListener('change', function() {
        //     report_type_id_value=SelectorGraph.value
        //     document.getElementById('id_report_type_id').value=report_type_id_value

        //     fetch('/GetReportDates',{
                
        //         method: 'POST',
        //         headers: {
        //             'Content-Type': 'application/json',
        //         },
        //         body: JSON.stringify(report_type_id_value)
        //     })
        //     .then(response => {

        //         return response.json();
        //     })
        //     .then(data => {
        //         console.log("Data received is",data)
        //         all_branches=document.getElementsByClassName('SingleBoxOverview')

        //         for (let index = 0; index < all_branches.length; index++) {

        //                 all_branches[index].style.display="none";
                    
        //         }

        //         id_report_to_select.innerHTML = "<option value=dummy selected disabled>Select Report for Displaying</option>"; //Removing all exisitng Options
        //         for (let index = 0; index < data.length; index++) {
                    
        //             newOption=document.createElement("option");
        //             newOption.value=data[index]
        //             newOption.text=data[index]
        //             id_report_to_select.appendChild(newOption);
        //         }

        //     });

        // })
        if(SelectorGraph){
        SelectorGraph.addEventListener('change', function(){
            document.getElementById('id_date_to').value = ""
            document.getElementById('id_date_from').value = ""
            var all_branches = document.getElementsByClassName('SingleBoxOverview');

            Array.from(all_branches).forEach(branch => {
                    branch.style.display = "none";
                    document.getElementById('All').style.display="none";

                })

        })
    }

        [document.getElementById('id_date_from'), document.getElementById('id_date_to')].forEach(function(element) {
            if (element) {
                element.addEventListener('change', function() {
                    const id_report_type_id = document.getElementById('id_report_type_id')?.value || "";
                    var id_date_from = document.getElementById('id_date_from')?.value || "";
                    var id_date_to = document.getElementById('id_date_to')?.value || "";
                    if(!id_date_from){
                        document.getElementById('id_date_to').value =  document.getElementById('id_date_from')?.value;
                        id_date_to=id_date_from
                    }
                    if (id_date_from && !id_date_to) {
                        document.getElementById('id_date_to').value =  document.getElementById('id_date_from')?.value;
                        id_date_to=id_date_from
                    }
                    // Validate values before sending the request
                    if (!id_date_from && !id_date_to) {
                        var all_branches = document.getElementsByClassName('SingleBoxOverview');

                        Array.from(all_branches).forEach(branch => {
                                branch.style.display = "none";
                                document.getElementById('All').style.display="none";
            
                        })
                        return;
                    }
                    else{
                        const report_full_date = [id_date_from,id_date_to, id_report_type_id];
                        console.log("Report full date is",report_full_date)
                        const all_branches = document.getElementsByClassName('SingleBoxOverview');
                        showLoading();
                        fetch('/GetBranchesForReport', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify(report_full_date),
                            
                        })
                            .then(response => response.json())
                            .then(data => {
                                console.log("DATA SENT TO BRANCHES IS:", data);
                                hideLoading();
                                let number_of_branches = 0;
    
                                Array.from(all_branches).forEach(branch => {
                                    console.log("single branch is",branch)
                                    if (data.includes(branch.textContent.trim())) {
                                        branch.style.display = "block";
                                        number_of_branches++;
                                    } else {
                                        branch.style.display = "none";
                                    }

                                    if (number_of_branches>0){
                                        document.getElementById('All').style.display="block";

                                    }
                                });
            
                                document.getElementById('All').style.display="block";
                                // Show "All" if multiple branches are visible
                                // document.getElementById('All').style.display = number_of_branches > 1 ? "block" : "none";
                            })
                            .catch(error => {
                                hideLoading();
                                alert("Error: Report with such date does not exist.");
                                console.error("Fetch failed:", error.message);
                            });
                        
                    }

        

                });
            }
        });
        

    }
    console.log("Graphs.js is working");

    //values here are not the text, but the values to be used for changing type of chart
    allowed_charts={
        "DataAggregation": ["pie", "doughnut", "bar", "line", "radar"],
        "BranchComparison":['bar', 'line', 'radar'],
        "PeriodComparison":['bar', 'line', 'radar']
    }
    const id_initial_chart_type=document.getElementById('id_initial_chart_type');

    if(id_initial_chart_type){

    const id_graph_element=document.getElementById('id_graph_element').getContext('2d');
    }

    const id_data_analysis_options=document.getElementById("id_data_analysis_options");
    if(id_data_analysis_options){
        id_data_analysis_options.onchange=function(){
            // alert(allowed_charts[id_data_analysis_options.value]);
            allowed_charts[id_data_analysis_options.value]

            Chart_Selector=document.getElementById('id_selector_chart_type');

            for (let index = 0; index < Chart_Selector.options.length; index++) {
                // console.log("Chart_Selector.options[index]",Chart_Selector.options[index].value)
                // console.log("allowed_charts[id_data_analysis_options.value]",allowed_charts[id_data_analysis_options.value])

                    if(allowed_charts[id_data_analysis_options.value].includes(Chart_Selector.options[index].value))
                    {
                        Current_Graph.destroy();
                        CreateGraph(id_graph_element,"bar");
                        id_initial_chart_type.value="bar";
                        Chart_Selector.value="bar";
                        Chart_Selector.options[index].style.display="block";
                    }

                    else{
                            Chart_Selector.options[index].style.display = 'none';

                    }
                
            }
        }
    }
    //Elements here
    const GraphsContainer=document.getElementsByClassName('GraphsContainer')[0];
    const id_selector_chart_type=document.getElementById('id_selector_chart_type');
    const id_simple_chart_full_screen_icon=document.getElementById('id_simple_chart_full_screen_icon');
    const id_simple_chart_zoom_out_screen_icon=document.getElementById('id_simple_chart_zoom_out_screen_icon');
    const id_graph_submit=document.getElementById('id_graph_submit');
    // const id_graph_dataset=document.getElementById('id_graph_dataset');
    if(GraphsContainer){

        if(id_simple_chart_full_screen_icon){
        id_simple_chart_full_screen_icon.addEventListener("click",function(event){
            selected_chart_type=id_selector_chart_type.value;
            ChartObject_Serialised=JSON.stringify(Current_Graph.config);
            table=document.getElementById('id_full_information_table')
            tabletwo=document.getElementById('id_full_information_table_two');
            id_expand_table=document.getElementById('id_expand_table');
            if(table.style.display==="table"){
                tabletwo.style.display="none";
                table.style.display="none";
                id_expand_table.style.display="none"
            }
            else{
                tabletwo.style.display="table";
                table.style.display="table";
                if(table.rows.length>=10){

                    id_expand_table.style.display="block"
                }

            }
            // id_graph_submit.submit();
            // location.replace("http://127.0.0.1:5000/Graph_Full_Screen");
        })
    }

    if(id_simple_chart_zoom_out_screen_icon){
        id_simple_chart_zoom_out_screen_icon.addEventListener("click",function(event){
            console.log("zoom out")
            location.replace("http://localhost:5000/Graph");
        })
    }





    Chart.register(ChartDataLabels);
    
    if(document.getElementById('id_graph_dataset')){

        dataset_element = JSON.parse(document.getElementById('id_graph_dataset').textContent);
    }
    selected_chart_type=id_initial_chart_type.value;

    // console.log("dataset element: " + dataset_element)
    if(id_graph_element){

    CreateGraph(id_graph_element,selected_chart_type);

    }
    if(id_selector_chart_type){
    id_selector_chart_type.addEventListener('change', function() {
        console.log(id_selector_chart_type.value)
        console.log("ID selector type chart is working");
        selected_chart_type=id_selector_chart_type.value;
        if(!Current_Graph){
        console.log("Current Graph IF statement executed")
        CreateGraph(id_graph_element,selected_chart_type,dataset_element);
        }
        else{
            console.log("Current Graph ELSE statement executed")

            Current_Graph.destroy();
            CreateGraph(id_graph_element,selected_chart_type,dataset_element);

        }
        



    });


}


console.log("Accessing current graph",Current_Graph)
function CreateGraph(id_graph_element,selected_chart_type,datasets_element){
    console.log("Data Received for new Report is",datasets_element)

   Current_Graph=new Chart(id_graph_element, {
    
        type: selected_chart_type,
        data: {
            labels: dataset_element.labels,
            datasets: [{
                label: '# Frequency',
                data: dataset_element.data.filter(value => value !== 0),
                backgroundColor: [
                    '#004B95',
                    '#06C',
                    '#519DE9',
                    '#8BC1F7',
                    '#F4C145',
                    '#F0AB00',
                    '#EC7A08'
                ],
                // borderColor: [
                //     'rgba(255, 99, 132, 1)',
                //     'rgba(54, 162, 235, 1)',
                //     'rgba(255, 206, 86, 1)',
                //     'rgba(75, 192, 192, 1)',
                //     'rgba(153, 102, 255, 1)',
                //     'rgba(255, 159, 64, 1)'
                // ],
                // borderColor:"white",
                // borderWidth: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                // title: 
                // {
                //     display: true,
                //     text: 'Specific Sale for GLOUCHESTOR RD',  // Title text
                //     font: {
                //         size: 17           // Title font size
                //     },
                // },
                tooltip: {
                    filter: (tooltipItem) => tooltipItem.raw !== 0 // Hide tooltips for 0 values
                  },
                  elements: {
                    arc: {
                      borderWidth: 1, // Ensure separation
                      borderColor: "#fff"
                    }
                  },
                  datalabels: {
                    display: (context) => context.raw > 0
                  },
                scales: {
                    x: {
                        ticks: {
                            callback: function(value, index, values) {
                                return value === "0.0" ? "" : value; // Hide zero labels
                            }
                        }
                    }
                },
                
                datalabels: {
                    align: 'center',
                    color: 'white',
                    backgroundColor:'black',
                    borderRadius:7,
                    font: {
                        weight: 'bold'
                    },
                    formatter: function(value, context) {
                        // console.log("Value for formatter is",value)
                        return  value;
                    }
                }
                
            }
        }
    });
}

    }
    else{
        console.log("Graph page did not load properly")
    }


});