//jQuery time
var current_fs, next_fs, previous_fs, step_ = 0; //fieldsets
var left, opacity, scale; //fieldset properties which we will animate
var animating; //flag to prevent quick multi-click glitches
var verified = false;
//$("#verify").attr("disabled", true)

function next() {
    if (animating) return false;
    animating = true;

    //if (step_ === 1 & !verified) return false;

    current_fs = $("fieldset").eq(step_);
    step_ += 1;
    next_fs = $("fieldset").eq(step_);

    //activate next step on progressbar using the step_
    $("#progressbar li").eq(step_).addClass("active");
    //show the next fieldset
    next_fs.show();
    //hide the current fieldset with style
    current_fs.animate({ opacity: 0 }, {
        step: function(now, mx) {
            //as the opacity of current_fs reduces to 0 - stored in "now"
            //1. scale current_fs down to 80%
            scale = 1 - (1 - now) * 0.2;
            //2. bring next_fs from the right(50%)
            right = (now * 50) + "%";
            //3. increase opacity of next_fs to 1 as it moves in
            opacity = 1 - now;
            current_fs.css({
                'transform': 'scale(' + scale + ')',
                'position': 'absolute'
            });
            next_fs.css({ 'right': right, 'opacity': opacity });
        },
        duration: 800,
        complete: function() {
            current_fs.hide();
            // reseting css
            current_fs.css({
                'transform': 'none',
                'position': 'relative'
            });
            animating = false;
        },
        //this comes from the custom easing plugin
        easing: 'easeInOutBack'
    });
}

function previous() {
    if (animating) return false;
    animating = true;

    current_fs = $("fieldset").eq(step_);
    previous_fs = $("fieldset").eq(0);

    //de-activate current and before steps on progressbar
    $("#progressbar li").each(function(i, e) { if (i > 0) $(e).removeClass('active') })

    //show the previous fieldset
    previous_fs.show();
    //hide the current fieldset with style
    current_fs.animate({ opacity: 0 }, {
        step: function(now, mx) {
            //as the opacity of current_fs reduces to 0 - stored in "now"
            //1. scale previous_fs from 80% to 100%
            scale = 0.8 + (1 - now) * 0.2;
            //2. take current_fs to the right(50%) - from 0%
            right = ((1 - now) * 50) + "%";
            //3. increase opacity of previous_fs to 1 as it moves in
            opacity = 1 - now;
            current_fs.css({ 'right': right });
            previous_fs.css({
                'transform': 'scale(' + scale + ')',
                'position': 'absolute',
                'opacity': opacity
            });
        },
        duration: 800,
        complete: function() {
            current_fs.hide();
            // reseting css
            current_fs.css({
                'transform': 'none',
                'position': 'relative'
            });
            animating = false;
        },
        //this comes from the custom easing plugin
        easing: 'easeInOutBack'
    });
    step_ = 0
}

$(".next").click(next);

$(".previous").click(previous);

$(".submit").click(function() {
    return false;
});