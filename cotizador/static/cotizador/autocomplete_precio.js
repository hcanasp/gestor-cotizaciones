// cotizador/static/cotizador/autocomplete_precio.js

document.addEventListener('DOMContentLoaded', (event) => {

    document.body.addEventListener('change', (e) => {

        if (e.target && e.target.name.endsWith('-producto')) {

            const productoId = e.target.value;
            if (!productoId) return;

            const rowId = e.target.name.split('-')[1];
            const precioInput = document.getElementById(`id_detalles-${rowId}-precio_unitario_capturado`);

            // ¡NUEVO! Buscamos el campo de garantía
            const garantiaInput = document.getElementById(`id_detalles-${rowId}-garantia_especifica_meses`);

            fetch(`/get_precio_producto/${productoId}/`)
                .then(response => response.json())
                .then(data => {
                    // Rellenamos el precio
                    if (data.precio && precioInput) {
                        precioInput.value = data.precio;
                    }

                    // ¡NUEVO! Rellenamos la garantía
                    if (data.garantia !== null && garantiaInput) {
                        garantiaInput.value = data.garantia;
                    }
                })
                .catch(error => console.error('Error:', error));
        }
    });
});