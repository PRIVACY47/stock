
USE [sm2]
GO
/****** Object:  Table [dbo].[category]    Script Date: 14-08-2023 23:20:09 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[category](
	[category_id] [int] IDENTITY(1,1) NOT NULL,
	[category_name] [varchar](50) NULL,
	[dated] [datetime] NULL,
 CONSTRAINT [PK_category] PRIMARY KEY CLUSTERED 
(
	[category_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[deleted_items]    Script Date: 14-08-2023 23:20:09 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[deleted_items](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[qr_id] [int] NULL,
	[item_name] [varchar](100) NULL,
	[category_id] [int] NULL,
	[user] [varchar](100) NULL,
	[type] [char](1) NULL,
	[dated] [datetime] NULL,
 CONSTRAINT [PK_deleted_items] PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[emp_master]    Script Date: 14-08-2023 23:20:09 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[emp_master](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[emp_id] [int] NULL,
	[emp_name] [varchar](50) NULL,
	[emp_mobile] [varchar](50) NULL,
	[emp_location] [varchar](50) NULL,
	[finger_print_id] [int] NULL,
	[dated] [datetime] NULL,
 CONSTRAINT [PK_emp_master] PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[emp_weapon_map]    Script Date: 14-08-2023 23:20:09 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[emp_weapon_map](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[category_id] [int] NULL,
	[qr_id] [int] NULL,
	[emp_id] [int] NULL,
	[finger_print_id] [int] NULL,
	[dated] [datetime] NULL,
 CONSTRAINT [PK_emp_weapon_map] PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[finger_data]    Script Date: 14-08-2023 23:20:09 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[finger_data](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[finger_print_id] [varchar](max) NULL,
	[emp_id] [int] NULL,
	[dated] [datetime] NULL,
 CONSTRAINT [PK_finger_data] PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[inventory_data]    Script Date: 14-08-2023 23:20:09 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[inventory_data](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[category_id] [int] NULL,
	[qty] [int] NULL,
	[qr_id] [int] NULL,
	[type] [char](1) NULL,
 CONSTRAINT [PK_inventory_data] PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[issue_inv]    Script Date: 14-08-2023 23:20:09 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[issue_inv](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[emp_id] [int] NULL,
	[category_id] [int] NULL,
	[qty] [int] NULL,
	[days] [int] NULL,
	[dated] [datetime] NULL,
	[finger_print_id] [int] NULL,
	[qr_id] [int] NULL,
	[issue_status] [varchar](8) NULL,
	[exp_status]  AS (case when getdate()>dateadd(day,[days],[dated]) then 'expired' else 'valid' end),
 CONSTRAINT [PK_issue_inv] PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[item]    Script Date: 14-08-2023 23:20:09 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[item](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[item_name] [varchar](50) NULL,
	[category_id] [int] NULL,
	[qr_id] [int] NULL,
	[status] [varchar](20) NULL,
	[assigned_status] [char](1) NULL,
	[type] [char](1) NULL,
	[qty] [int] NULL,
	[dated] [datetime] NULL,
 CONSTRAINT [PK_item] PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[receive_inv]    Script Date: 14-08-2023 23:20:09 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[receive_inv](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[category_id] [int] NULL,
	[qty] [int] NULL,
	[finger_print_id] [int] NULL,
	[emp_id] [int] NULL,
	[dated] [datetime] NULL,
	[qr_id] [int] NULL,
 CONSTRAINT [PK_receive_inv] PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[receive_stock]    Script Date: 14-08-2023 23:20:09 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[receive_stock](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[category_id] [int] NULL,
	[qr_id] [int] NULL,
	[qty] [int] NULL,
	[vendor] [varchar](50) NULL,
	[deliv_partner] [varchar](50) NULL,
	[remarks] [varchar](max) NULL,
	[dated] [datetime] NULL,
 CONSTRAINT [PK_receive_stock] PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[request_stock]    Script Date: 14-08-2023 23:20:09 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[request_stock](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[category_id] [int] NULL,
	[qr_id] [int] NULL,
	[qty] [int] NULL,
	[remarks] [varchar](max) NULL,
	[dated] [datetime] NULL,
 CONSTRAINT [PK_request_stock] PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
/****** Object:  Table [dbo].[transaction_data]    Script Date: 14-08-2023 23:20:09 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[transaction_data](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[emp_id] [int] NULL,
	[category_id] [int] NULL,
	[qty] [int] NULL,
	[days] [int] NULL,
	[dated] [datetime] NULL,
	[finger_print_id] [int] NULL,
	[qr_id] [int] NULL,
	[type_of_tx] [char](1) NULL,
 CONSTRAINT [PK_transaction_data] PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[user_man]    Script Date: 14-08-2023 23:20:09 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[user_man](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[userid] [varchar](50) NULL,
	[password] [varchar](100) NULL,
	[name] [varchar](50) NULL,
	[empid] [varchar](12) NULL,
	[location] [varchar](50) NULL,
	[status] [char](1) NULL,
	[dated] [datetime] NULL,
 CONSTRAINT [PK_user_man] PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[weapon_assign]    Script Date: 14-08-2023 23:20:09 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[weapon_assign](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[category_id] [int] NULL,
	[qr_id] [int] NULL,
	[qty] [int] NULL,
	[emp_id] [int] NULL,
	[finger_print_id] [int] NULL,
	[dated] [datetime] NULL,
 CONSTRAINT [PK_weapon_assign] PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
ALTER TABLE [dbo].[category] ADD  CONSTRAINT [DF_category_dated]  DEFAULT (getdate()) FOR [dated]
GO
ALTER TABLE [dbo].[deleted_items] ADD  CONSTRAINT [DF_deleted_items_dated]  DEFAULT (getdate()) FOR [dated]
GO
ALTER TABLE [dbo].[emp_master] ADD  CONSTRAINT [DF_emp_master_dated]  DEFAULT (getdate()) FOR [dated]
GO
ALTER TABLE [dbo].[emp_weapon_map] ADD  CONSTRAINT [DF_emp_weapon_map_dated]  DEFAULT (getdate()) FOR [dated]
GO
ALTER TABLE [dbo].[finger_data] ADD  CONSTRAINT [DF_finger_data_dated]  DEFAULT (getdate()) FOR [dated]
GO
ALTER TABLE [dbo].[issue_inv] ADD  CONSTRAINT [DF_issue_inv_dated]  DEFAULT (getdate()) FOR [dated]
GO
ALTER TABLE [dbo].[item] ADD  CONSTRAINT [DF_item_dated]  DEFAULT (getdate()) FOR [dated]
GO
ALTER TABLE [dbo].[receive_inv] ADD  CONSTRAINT [DF_receive_inv_dated]  DEFAULT (getdate()) FOR [dated]
GO
ALTER TABLE [dbo].[receive_stock] ADD  CONSTRAINT [DF_receive_stock_dated]  DEFAULT (getdate()) FOR [dated]
GO
ALTER TABLE [dbo].[request_stock] ADD  CONSTRAINT [DF_request_stock_dated]  DEFAULT (getdate()) FOR [dated]
GO
ALTER TABLE [dbo].[transaction_data] ADD  CONSTRAINT [DF_transaction_data_dated]  DEFAULT (getdate()) FOR [dated]
GO
ALTER TABLE [dbo].[user_man] ADD  CONSTRAINT [DF_user_man_dated]  DEFAULT (getdate()) FOR [dated]
GO
ALTER TABLE [dbo].[weapon_assign] ADD  CONSTRAINT [DF_weapon_assign_dated]  DEFAULT (getdate()) FOR [dated]
GO
USE [master]
GO
ALTER DATABASE [stock_management] SET  READ_WRITE 
GO
