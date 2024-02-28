
document.addEventListener("DOMContentLoaded", function() {


// Crear un array para almacenar los próximos 6 días
let stringDataArray = [];

// Obtener la fecha de hoy con Moment.js
let hoy = moment();

// Iterar para los próximos 6 días, excluyendo los Lunes
for (let i = 0; i < 6; i++) {
    // Crear un objeto para el día actual
    let dia = {
        nombreStr: hoy.format('ddd'), // Obtener el nombre abreviado del día de la semana (Ej: Lun, Mar, ...)
        numeroStr: hoy.format('DD'),  // Obtener el número del día del mes (Ej: 26, 27, ...)
        mesStr: hoy.format('MMM')     // Obtener el nombre abreviado del mes (Ej: Feb, Mar, ...)
    };

    // Agregar el objeto al array de los próximos 6 días
    stringDataArray.push(dia);

    // Añadir un día para el siguiente ciclo
    hoy.add(1, 'days');
}

   // Supongamos que tienes el array de objetos next6days como lo definiste antes

let datesList = document.querySelector(".dates-list");

// Itera sobre el array stringDataArray
for (let i = 0; i < stringDataArray.length; i++) {
    let dia = stringDataArray[i];

    // Crea elementos de span para cada parte de la fecha
    let spanDay = document.createElement("span");
    spanDay.classList.add("text-nombre-dia");
    spanDay.textContent = dia.nombreStr;

    let spanDate = document.createElement("span");
    spanDate.classList.add("numero-dia");
    spanDate.textContent = dia.numeroStr;

    let spanMonth = document.createElement("span");
    spanMonth.classList.add("texto-mes");
    spanMonth.textContent = dia.mesStr;

    // Crea el botón y añade los spans
    let button = document.createElement("button");
    button.classList.add("btn-fecha");
    button.appendChild(spanDay);
    button.appendChild(document.createElement("br")); // Salto de línea
    button.appendChild(spanDate);
    button.appendChild(document.createElement("br")); // Salto de línea
    button.appendChild(spanMonth);

    // Crea el elemento de la lista y añade el botón
    let li = document.createElement("li");
    li.appendChild(button);

    // Añade el elemento de la lista a la lista de fechas
    datesList.appendChild(li);
}




});
