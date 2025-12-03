// cotizador/static/cotizador/cotizacion_admin.js

document.addEventListener('DOMContentLoaded', function () {
    console.log('Script cotizacion_admin.js cargado correctamente.');
    alert('Script cargado: cotizacion_admin.js');

    const inputTRM = document.getElementById('id_trm');

    if (inputTRM) {
        // Crear el botón
        const btnActualizar = document.createElement('button');
        btnActualizar.type = 'button';
        btnActualizar.innerText = 'Actualizar TRM';
        btnActualizar.style.marginLeft = '10px';
        btnActualizar.classList.add('button'); // Clase estilo Django admin

        // Insertar el botón después del input
        inputTRM.parentNode.insertBefore(btnActualizar, inputTRM.nextSibling);

        // Evento click
        btnActualizar.addEventListener('click', function () {
            fetch('/get_trm_actual/')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Error en la respuesta de la red');
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.trm) {
                        inputTRM.value = data.trm;
                        console.log('TRM actualizada a:', data.trm);
                    } else {
                        console.error('No se encontró el valor de TRM en la respuesta');
                    }
                })
                .catch(error => {
                    console.error('Hubo un problema con la petición fetch:', error);
                    alert('Error al actualizar la TRM. Revisa la consola.');
                });
        });
    } else {
        console.warn('No se encontró el input con id="id_trm"');
    }
});