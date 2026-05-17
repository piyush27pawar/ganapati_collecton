function addCollection() {

    let name = document.getElementById("name").value;
    let amount = document.getElementById("amount").value;

    if(name == "" || amount == ""){
        alert("Fill all fields");
        return;
    }

    let table = document.getElementById("table");

    let row = table.insertRow();

    let cell1 = row.insertCell(0);
    let cell2 = row.insertCell(1);

    cell1.innerHTML = name;
    cell2.innerHTML = "₹" + amount;

    document.getElementById("name").value = "";
    document.getElementById("amount").value = "";
}