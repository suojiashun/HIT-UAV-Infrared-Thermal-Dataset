{

"info": 

	{
	
	"year": int,
	
	"version": int,
	
	"description": str,
	
	"contributor": str,
	
	"url": str,
	
	"data_created": str
	
	},

"licenses":

	{
	
	"url": str,
	
	"id": str,
	
	"name": str
	
	},

"scenarios":

	[{
	
	"id": int,
	
	"name": str
	
	}],

"weather":

```
[{

"id": int,

"name": str

}]
```

"images":

	[{
	
	"id": int,
	
	"width": int,
	
	"height": int,
	
	"file_name": str,
	
	"scenario": int,
	
	"weather": int,
	
	"perspective": int,
	
	"altitude": int,
	
	"license": int,
	
	"data_captured": date	
	
	}],

"categories":

	[{
	
	"id": int,
	
	"name": str
	
	}],

"annotations":

	[{
	
	"id": int,
	
	"image_id": int,
	
	"category_id": int,
	
	"difficult": bool,
	
	"truncated": "bool",
	
	"bbox": [xmin, ymin, width, height, angle]
	
	}]

}