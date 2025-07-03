function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

function updateCartCount(cart) {
    let total = 0;
    for (const qty of Object.values(cart)) {
        total += qty;
    }
    $('#cart-count').text(total);
}

$(document).ready(function() {
    $.get('/store/cart/data/', function(response) {
        updateCartCount(response.cart);
    });

    $('.add-to-cart').click(function() {
        const productId = $(this).data('id');

        $.ajax({
            url: '/store/add/',
            method: 'POST',
            data: {
                'product_id': productId,
                'csrfmiddlewaretoken': getCSRFToken()
            },
            success: function(response) {
                updateCartCount(response.cart);

                const toastEl = document.getElementById('cartToast');
                const toast = new bootstrap.Toast(toastEl);
                toast.show();
            },
            error: function() {
                alert('Failed to add to cart.');
            }
        });
    });
});