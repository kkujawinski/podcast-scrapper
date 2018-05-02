django.jQuery(function() {
    if( typeof(jsoneditor) == "undefined" )
        jsoneditor = { JSONEditor:JSONEditor };
    setInterval(function(){
        var fields = django.jQuery(".for_jsoneditor");
        for(var i=0; i < fields.length; i++) {
            var $f = django.jQuery(fields[i]);
            var id = $f.attr("id") + "_jsoneditor";
            var name = $f.attr("name") + "_jsoneditor";
            var $nxt = $f.parent().find('#'+id);
            if($nxt.hasClass('with_modes')) {
                continue;
            }

            $nxt.remove()

            var value = {};
            try {
                value = JSON.parse($f[0].value);
            } catch(e) {
                // ignore
            }
            $nxt.detach();
            $nxt = django.jQuery('<div cols="40" rows="10" id="'+id+'" name="'+name+'" class="with_modes"></div>');
            $f.parent().append($nxt);
            var fnc = function(f,nxt,value) {

                var editor = new jsoneditor.JSONEditor(nxt,{
                    change:function() {
                        f.value = JSON.stringify(editor.get());
                    },
                    modes: ['tree', 'text']
                },value);
            }($f[0],$nxt[0],value);
        }
    },12);
});