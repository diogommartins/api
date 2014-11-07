/**
 * Created by diogomartins on 11/7/14.
 */
$(window).bind('scroll', function() {

            if ($(this).scrollTop() > 100) {

                $('div.navbar').css({
                    position: 'fixed',
                    top: '0px',
                    width: '100%',
                    opacity: '.9'
                });


            } else {

                $('div.navbar').css({
                    position: 'relative',
                    top: '0px',
                    width: 'auto',
                    opacity: '1'
                });

            }
        });