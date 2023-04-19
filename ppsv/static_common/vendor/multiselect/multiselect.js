function move_remove_all(where,list_id)
{
	if (where == 'right')
	{
		$('#' + list_id + ' #id_multivalfrom').find('option').each(function(){
			var optionval = '<option value="'+$(this).val()+'">'+$(this).html()+'</option>';
			$('#' + list_id).find('#id_multivalto').append(optionval);
		});
		$('#' + list_id + ' #id_multivalfrom').html('');
	}
	else if (where == 'left')
	{
		$('#' + list_id + ' #id_multivalto').find('option').each(function(){
			var optionval = '<option value="'+$(this).val()+'">'+$(this).html()+'</option>';
			$('#' + list_id).find('#id_multivalfrom').append(optionval);
		});
		$('#' + list_id + ' #id_multivalto').html('');
	}
}
function top_bottom(where,list_id)
{
	var selected = $('#' + list_id + ' #id_multivalto').val();
	var appendvalue = '';
	for (i=0;i<selected.length;i++)
	{
		appendvalue += '<option value="'+selected[i]+'">'+selected[i]+'</option>';
		$('#' + list_id + ' #id_multivalto option[value="'+selected[i]+'"]').remove();
	}
	if (where == 'top')
	{
		$('#' + list_id + ' #id_multivalto').prepend(appendvalue);
	}
	else if (where == 'bottom')
	{
		$('#' + list_id + ' #id_multivalto').append(appendvalue);
	}
};
function up_down(where,list_id)
{
	var $op = $('#' + list_id + ' #id_multivalto option:selected');
	if($op.length)
	{
		if(where == 'up')
		{
			$op.first().prev().before($op)
		}
		else if (where == 'down')
		{
			$op.last().next().after($op);
		}
	}
}
function move_remove(where,list_id)
{
	if (where == 'right')
	{
		var selected = $('#' + list_id).find('#id_multivalfrom').val();
		var appendvalue = ''
		for (i=0;i<selected.length;i++)
		{
			let to_remove = $('#' + list_id).find('#id_multivalfrom option[value="'+selected[i]+'"]');
			appendvalue += '<option value="'+selected[i]+'">'+to_remove.html()+'</option>';
			to_remove.remove();
		}
		$('#' + list_id).find('#id_multivalto').append(appendvalue);
	}
	else if (where == 'left')
	{
		var selected = $('#' + list_id).find('#id_multivalto').val();
		var appendvalue = ''
		for (i=0;i<selected.length;i++)
		{
			let to_remove = $('#' + list_id).find('#id_multivalto option[value="'+selected[i]+'"]');
			appendvalue += '<option value="'+selected[i]+'">'+to_remove.html()+'</option>';
			to_remove.remove();
		}
		$('#' + list_id).find('#id_multivalfrom').append(appendvalue);
	}
}
function assign_btn_action(list_id)
{
	$("#" + list_id).find("#top_btn")[ 0 ].onclick = function() {
		top_bottom('top',list_id);
	};
	$("#" + list_id).find("#bottom_btn")[ 0 ].onclick = function() {
		top_bottom('bottom',list_id);
	};
	$("#" + list_id).find("#up_btn")[ 0 ].onclick = function() {
		up_down('up',list_id);
	};
	$("#" + list_id).find("#down_btn")[ 0 ].onclick = function() {
		up_down('down',list_id);
	};
	$("#" + list_id).find("#move_btn")[ 0 ].onclick = function() {
		move_remove('right',list_id);
	};
	$("#" + list_id).find("#remove_btn")[ 0 ].onclick = function() {
		move_remove('left',list_id);
	};
	$("#" + list_id).find("#move_all_btn")[ 0 ].onclick = function() {
		move_remove_all('right',list_id);
	};
	$("#" + list_id).find("#remove_all_btn")[ 0 ].onclick = function() {
		move_remove_all('left',list_id);
	};
}

function getvalue(list_id)
{
	var values = '';
	$("#" + list_id + " #id_multivalto").find("option").each(function(){
		values += $(this).html() + ',';
	});
	values = values.substr(0,values.lastIndexOf(','));
	return values;
}
