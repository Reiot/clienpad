function add_post(board, $posts, data){
	var i;
	for( i = 0 ; i < data.length ; i ++ ){
		var post = data[i];
		var li = '<li>'
		+ post.author
		+ '<a href="/' + board + '/' + post.id + '">' 
		+ post.title 
		+ '<span class="ui-li-aside ui-li-desc">' + post.publish_time_short + '</span>'
		+ '</a>';
		if(post.comments>0){
			li += '<span class="ui-li-count">' + post.comments + '</span>';
		}					
		li += '</li>';					
		
		$posts.append(li);
	}
	$posts.listview('refresh');
	
}

$(function(){
	
	$('a.refresh').live('click', function(){
		var $button = $(this),
			board = $button.data('board');
			
		console.log('board', board);
		
		var $posts = $button.parents('div[data-role="page"]').find('ul.posts');
		$posts.empty();

		$.mobile.pageLoading();

		$.getJSON("/"+board, { format: "json" })
			.success(function(response){
				console.log('response',response);
				add_post(board, $posts, response.posts);
			})
			.complete(function(){
				$.mobile.pageLoading(true);
			});
	});
	
	$('a.more').live('click', function(){
		var $button = $(this),
			board = $button.data('board'),
			nextPage = $button.data('next-page');
			
		console.log('board', board, 'nextPage', nextPage);
		
		var $posts = $button.parents('div[data-role="page"]').find('ul.posts');		
		$.mobile.pageLoading();
		
		$.getJSON("/"+board+"/page"+nextPage, { format: "json" })
			.success(function(response){
				console.log('response',response);
				
				$button.data('next-page', response.next_page);
				var i;
				for( i = 0 ; i < response.posts.length ; i ++ ){
					var post = response.posts[i];
					var li = '<li>'
					+ post.author
					+ '<a href="/' + board + '/' + post.id + '">' 
					+ post.title 
					+ '<span class="ui-li-aside ui-li-desc">' + post.publish_time_short + '</span>'
					+ '</a>';
					if(post.comments>0){
						li += '<span class="ui-li-count">' + post.comments + '</span>';
					}					
					li += '</li>';					
					
					$posts.append(li);
				}
				$posts.listview('refresh');
			})
			.complete(function(){
				$.mobile.pageLoading(true);
				//$.mobile.silentScroll(100);	
			});
	});
});